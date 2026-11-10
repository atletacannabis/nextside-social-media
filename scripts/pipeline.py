#!/usr/bin/env python3
"""Valida um lote, prepara chamadas ao Buffer e registra resultados sem repetir posts."""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(dir=path.parent, prefix='.writing-')
    try:
        with os.fdopen(handle, 'w') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def load_batch(path):
    batch = read_json(path)
    seen = set()
    for post in batch['posts']:
        key = post['key']
        if key in seen:
            raise ValueError(f'Chave repetida: {key}')
        seen.add(key)
        if not post['caption'].strip() or len(post['caption']) > 2200:
            raise ValueError(f'Legenda ausente ou longa: {key}')
        if not 1 <= len(post['images']) <= 10:
            raise ValueError(f'Quantidade de imagens inválida: {key}')
        if post['mode'] not in ('shareNow', 'customScheduled'):
            raise ValueError(f'Modo inválido: {key}')
        if post['mode'] == 'customScheduled':
            date = datetime.fromisoformat(post['dueAt'].replace('Z', '+00:00'))
            if date.utcoffset() is None:
                raise ValueError(f'Horário sem fuso: {key}')
        for image in post['images']:
            path = (ROOT / image).resolve()
            if not path.is_relative_to(ROOT):
                raise ValueError(f'Imagem fora do repositório: {image}')
            if not path.is_file() or not path.read_bytes().startswith(b'\xff\xd8'):
                raise ValueError(f'JPG ausente ou inválido: {image}')
            if path.stat().st_size > 8 * 1024 * 1024:
                raise ValueError(f'Imagem acima de 8 MB: {image}')
    return batch


def fingerprint(post):
    data = dict(post)
    data['imageHashes'] = [hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in post['images']]
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['validate', 'prepare', 'record'])
    parser.add_argument('batch', type=Path)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--key')
    parser.add_argument('--post-id')
    parser.add_argument('--status', choices=['sent', 'scheduled', 'sending', 'draft', 'error'])
    args = parser.parse_args()
    batch = load_batch(args.batch)
    state = read_json(args.state) if args.state.exists() else {}
    if args.action == 'record':
        post = next(p for p in batch['posts'] if p['key'] == args.key)
        if not args.post_id or not args.status:
            parser.error('record exige --key, --post-id e --status')
        old = state.get(args.key)
        if old and old['postId'] != args.post_id:
            raise ValueError('Já existe um post com esta chave. Confira no Buffer antes de continuar.')
        state[args.key] = {'postId': args.post_id, 'status': args.status, 'fingerprint': fingerprint(post), 'recordedAt': datetime.now(timezone.utc).isoformat()}
        write_json(args.state, state)
        print(json.dumps({'recorded': args.key, 'status': args.status}))
        return
    if args.action == 'validate':
        print(json.dumps({'posts': len(batch['posts']), 'images': sum(len(p['images']) for p in batch['posts'])}))
        return
    if not args.output:
        parser.error('prepare exige --output')
    sha = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    requests = []
    for post in batch['posts']:
        key = post['key']
        previous = state.get(key)
        if previous:
            if previous['fingerprint'] != fingerprint(post):
                raise ValueError(f'Post registrado foi alterado: {key}. Edite pelo ID do Buffer.')
            continue
        if post['mode'] == 'customScheduled' and datetime.fromisoformat(post['dueAt'].replace('Z','+00:00')) <= datetime.now(timezone.utc):
            raise ValueError(f'Agendamento no passado: {key}')
        for image in post['images']:
            committed = subprocess.check_output(['git','-C',str(ROOT),'show',f'{sha}:{image}'])
            if committed != (ROOT / image).read_bytes():
                raise ValueError(f'Imagem ainda não foi commitada: {image}')
        payload = {'channelId': post['channelId'], 'text': post['caption'], 'schedulingType': 'automatic', 'mode': post['mode'], 'assets': [{'image': {'url': f"https://raw.githubusercontent.com/{batch['repository']}/{sha}/{p}", 'metadata': {'altText': f"NextSide | {post['key']} | card {i+1}"}}} for i,p in enumerate(post['images'])], 'metadata': {'instagram': {'type': 'post', 'shouldShareToFeed': True, 'isAiGenerated': post.get('isAiGenerated',False), 'firstComment': post['firstComment']}}}
        if post['dueAt']:
            payload['dueAt'] = post['dueAt']
        requests.append({'key': key, 'fingerprint': fingerprint(post), 'arguments': payload})
    write_json(args.output, {'organizationId': batch['organizationId'], 'requests': requests})
    print(json.dumps({'prepared': len(requests), 'skippedRecorded': len(batch['posts'])-len(requests), 'output': str(args.output)}))


if __name__ == '__main__':
    main()
