# Mr_Bot
# # Automação que rastreia sites de notícias, resume os textos com IA e faz a postagem em um site.

- Esta automação cria uma news letter para meu [Portfólio](https://www.brainstormtech.com.br/) usando Web Scraping, para rastrear conteúdo na internet e IA para resumir os textos da news letter.
- [Aqui](https://github.com/Fat83dotcom/Mr_Bot/blob/master/article_crawler.py) eu apresento o algoritmo isolado, pois o mesmo é integrado com o aplicativo do site e o banco de dados da aplicação, entretanto o algoritmo pode ser aproveitado e testado e aqui vou sugerir como fazer isso.
- Eu criei uma tabela em um banco de dados SQL para armazenar os metadados que o bot usa para rastrear.

```sql
CREATE TABLE register_sites (
    id SERIAL PRIMARY KEY,
    site_name VARCHAR(255) DEFAULT '' NOT NULL,
    search_url VARCHAR(255) DEFAULT '' NOT NULL,
    search_result_selector VARCHAR(255) DEFAULT '' NOT NULL,
    title_selector VARCHAR(255) DEFAULT '' NOT NULL,
    content_selector VARCHAR(255) DEFAULT '' NOT NULL,
    topic VARCHAR(100) DEFAULT '' NOT NULL,
    n_links INTEGER DEFAULT 0 NOT NULL,
    link_complement VARCHAR(255) DEFAULT '' NOT NULL,
    is_absolute_url VARCHAR(5) DEFAULT 'True' NOT NULL,
    url_pattern VARCHAR(255) DEFAULT '' NOT NULL
);
```

- Basta conectar um banco de dados que contenha esta tabela que o bot ira recuperar os metadados.[Aqui](https://github.com/Fat83dotcom/Mr_Bot/blob/master/automation_db.py) eu busquei os dados do banco com variaveis de ambiente, mas se você quiser é só forncer os dados do banco diretamente.
-Aqui vai um exemplo que uso no meu caso e uma explicação de como o rastreio funciona.

- 1 - 'G1',
- 2 - 'https://g1.globo.com/busca/?q=',
- 3 - 'div.widget--info__text-container a',
- 4 - 'div.title h1.content-head__title',
- 5 - 'div.content-text p.content-text__container',
- 6 - 'tecnologia',
- 7 - 2,
- 8 - 'https:',
- 9 - False,
- 10 - r"u=([^&]+)"

A sequencia é correspondente a tabela.

1 é o nome do site ou portal.

2 é a URL de onde parte a busca. Nesse caso é uma URL de pesquisa e o assunto buscado pode ser escolhido. Dependendo do site, essa busca pode ser realizada pelo Google, por exemplo, sendo impossivel prever o resultado. Quando isso ocorre, pode ser passado uma página onde contém as ocorrencias procuradas, é o mesmo principio da busca. Nesse ponto estamos buscando uma página que contenha uma lista de páginas de assuntos buscados.

3 São os seletores CSS que contem os links para as paginas alvo. 'div.widget--info__text-container' é uma div pai de onde se encontram as tags 'a'. O restrador vai obter todas as ocorrencias de 'a', que são os caminhos para as páginas de interesse.

4 Este seletor recupera o titulo da página alvo. É indicado ao crawler o seletor pai e o selecor alvo.

5 É o seletor onde o conteudo se encontra. Neste ponto, muita sujeira é recuperada; paragrafos de anucios e outros assuntos que não estão no escopo, mas fique tranquilo, a IA vai nos ajudar a resolver isso. É indicado ao crawler o seletor pai e o selecor alvo.

6 Quando a página de busca é personalizada pelo site, você pode escolher um assunto, desde que ele exista no conteudo, é claro, para que o rastreador direcione a busca corretamente. Se o site possuir um buscador do tipo Google, essa parte pode ser omitida e a página de assunto pode ser definida manualmente no item 2.

7 Define a quantidade de páginas alvo que serão buscadas dentro da pagina de busca. Existe uma lógica no algoritmo que limita essa busca, logo, a quantidade de busca é limitada pelo máximo retornado pelo site, caso você descoheça a quantidade retornada.

8 Alguns sites disponibilizam somente os caminhos relativos quando geram suas buscas, isso é comum. Você deverá verificar o tipo de retorno e se necessário adicionar o URL necessário para o rastreador continuar a recuperar. Este complemente, se for usado, virá sempre antes do caminho relativo, geramente será o endereço do site, sempre verifique com cuidado essa parte, pois se não for retornado um link válido, o algoritmo não vai retornar nada.

9 Use True se o caminho for absoluto e False se for usar o complemento.

10 Este é um caso especial onde o site retorna um link que engana seu robô. o link se parece com isso: https://g1.globo.com/busca/click?q=tecnologia&p=1&r=1724522800067&u=https%3A%2F%2Fgloboplay.globo.com%2Fv%2F12847167%2F&syn=False&key=f21f2df7300adb7400db720232211585. Este link retorna um conteudo inutil, mas nele existe o link aboluto, que pode ser extraido e usado para acessar a página alvo. Aqui é usado uma expressão regular que captura esta parte: u=https%3A%2F%2Fgloboplay.globo.com%2Fv%2F12847167%2F, e um parse do urllib converte este padrão em um padrão ASCII. Este regex deve ser usado somente em casos semelhantes e deve ser adequado ao caso de uso.

- Após a parte do rastreador fazer seu trabalho, é necessário tratar esses dados. Em outros tempos, esse trabalho poderia ser pesado, imagina tentar resumir um texto usando algoritmos? Mas a nossa sorte é que não estamos mais nesse tempo e hoje temos as IA's, que são ferramentas incríveis para esse tipo de problema. O texto recuperado não vem muito limpo, está repleto de retorno de carro, emojes e outros caracteres indesejaveis. Nesse projeto usei o Gemini do Google, o engine "gemini-1.5-flash", primeiro por ter uma API muito simples e segundo por ser gratuito, claro que bem restritivo, mas pra esse projeto serve muito bem.
- O próximo passo é a entrada de dados na IA e o prompt. O prompt que estou usando nesse momento, está embutido no código, e deixarei ele para eventuais consultas. Ele deve ser bem claro e detalhado.Nesse caso, para saida de dados estou usando a propria saida da IA diretamente. Eu pensei que isso poderia ser um problema, afinal, confiar uma saida de dados a uma IA generativa, me parece uma ideia maluca, mas durante o desenvolvimento, que durou 5 dias, ela sempre retornou o que eu pedi e o programa nunca falhou por isso, entretando, posteriormente implementarei um verificador para isto. Ela retona uma lista de dicionarios, só que em str, e isso não serve pra nada. então usei um recurso interessante do Python que é ast.literal_eval(), da lib ast, que identifica e estrutura de dados na string e converte para uma estrutura de dados válida, isso é tão util, que dá vontade de chorar de alegria.
- A saida de dados é concluida em pipe_line_9, na classe Bot, no metodo run(), a aprtir desse ponto, as particularidades são relativas ao aplicativo que integrei o bot, e não vou especifica-las aqui.
- O resultado pode ser acessado no meu [Portfólio](https://www.brainstormtech.com.br/), na seção Artigos.