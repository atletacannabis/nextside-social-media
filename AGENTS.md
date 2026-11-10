# Publicações da NextSide

Use este repositório para novos lotes de Instagram. Hospede somente artes aprovadas e conteúdo destinado ao público. Mantenha credenciais fora do repositório.

## Destino

- Organização Buffer Atleta Cannabis, ID `6ad8ce63a88463d5ffba068f`.
- Instagram `nextside.tech`, canal `6af3286462b70b94b0e2f31d`.
- Hospedagem pública exclusiva `atletacannabis/nextside-social-media`.
- Confirme a conexão do canal antes de criar um novo lote.

## Procedimento

1. Leia o lote em `batches/` e o registro correspondente em `history/`. A autorização de publicação vale para o lote indicado pelo usuário.
2. Consulte os posts do canal no Buffer antes de enviar. Reconcilie qualquer chamada com resultado incerto usando o conteúdo e o canal antes de tentar criar outro post.
3. Valide JPGs e legendas com `scripts/pipeline.py validate`. Confirme datas, fuso e ordem dos cards.
4. Faça commit e push das artes. Use `pipeline.py prepare` para obter URLs imutáveis do commit e argumentos para o conector Buffer. Verifique os links sem autenticação.
5. Execute `buffer.create_post` em ordem com os argumentos preparados. Registre cada ID imediatamente com `pipeline.py record`, usando o mesmo arquivo de estado em todo o lote.
6. Consulte `buffer.get_post` ou `buffer.list_posts` para confirmar que os posts imediatos chegaram a `sent` e que os futuros estão `scheduled` nas datas corretas. Atualize o histórico com os estados finais.
7. Salve o histórico confirmado em `history/` e faça commit e push. Informe qualquer falha pendente e os horários efetivos ao usuário.

A publicação automática de carrosséis usa legenda e primeiro comentário. Música requer finalização pelo Instagram e deve ser decidida com o usuário antes de mudar o modo de publicação. Para o lote de novembro, o usuário escolheu publicação automática.

Se o texto ou as imagens de uma chave registrada mudarem, revise o post já existente pelo ID. Não crie outro post para contornar uma falha. Preserve os arquivos públicos referenciados por posts já criados.
