# Publicações NextSide

Artes públicas e preparação dos lotes de Instagram da @nextside.tech.

## Novo lote

1. Salve os JPGs em uma pasta exclusiva, com nomes de card em ordem.
2. Copie o modelo de `batches/novembro-2026.json` para um novo arquivo. Preencha legenda, primeiro comentário, imagens e horários com fuso. Cada post precisa de uma chave única.
3. Valide o lote com o comando abaixo e faça commit e push das artes. Os links públicos usam o SHA do commit para preservar a versão aprovada.
4. Prepare as chamadas ao Buffer. Use o conector para executar os argumentos de cada pedido, em ordem. Confira o canal e a autorização de publicação do lote.
5. Registre cada ID retornado imediatamente. Depois confirme o status pelo Buffer e atualize o registro. Se uma chamada tiver resultado incerto, consulte o canal antes de tentar criar o post outra vez.

```sh
python3 scripts/pipeline.py validate batches/novembro-2026.json --state /tmp/nextside-history.json
python3 scripts/pipeline.py prepare batches/novembro-2026.json --state /tmp/nextside-history.json --output /tmp/nextside-requests.json
python3 scripts/pipeline.py record batches/novembro-2026.json --state /tmp/nextside-history.json --key novembro-2026-01 --post-id ID_RETORNADO --status sent
```

A preparação ignora as chaves já registradas. Uma alteração em post registrado exige revisar o ID existente no Buffer. Guarde o histórico confirmado em `history/` ao concluir o lote. Credenciais e chaves de API ficam fora deste repositório.

## Padrão atual

- JPG vertical de 1080 × 1350 px, em ordem numérica.
- Legenda comercial, primeiro comentário com uma pergunta e menções relacionadas ao tema.
- Fuso America/Sao_Paulo. No lote atual, 13h corresponde a 16h UTC.
- Publicação automática. Música em carrosséis exige finalização manual no Instagram.
- Antes de publicar, revisar condições comerciais, direitos das imagens, perfil, datas e duplicatas no canal.

A publicação usa o conector Buffer. O script prepara as chamadas e registra as respostas, sem precisar guardar credenciais do Buffer no GitHub.
