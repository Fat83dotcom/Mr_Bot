# Mr_Bot
## Automação que rastreia sites de notícias, resume os textos com IA e faz a postagem em um site.

- Esta automação cria uma newsletter para meu [Portfólio](https://www.brainstormtech.com.br/) usando Web Scraping para rastrear conteúdo na internet e IA para resumir os textos da newsletter.
- [Aqui](https://github.com/Fat83dotcom/Mr_Bot/blob/master/article_crawler.py) eu apresento o algoritmo isolado, pois o mesmo é integrado com o aplicativo do site e o banco de dados da aplicação. Entretanto, o algoritmo pode ser aproveitado e testado, e aqui vou sugerir como fazer isso.
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
- Basta conectar a um banco de dados que contenha esta tabela, e o bot irá recuperar os metadados. [Aqui](https://github.com/Fat83dotcom/Mr_Bot/blob/master/automation_db.py) eu busco os dados do banco com variáveis de ambiente, mas se você quiser, é só fornecer os dados do banco diretamente.
Aqui vai um exemplo que uso no meu caso e uma explicação de como o rastreamento funciona:

- 1 - 'G1'

- 2 - 'https://g1.globo.com/busca/?q='

- 3 - 'div.widget--info__text-container a'

- 4 - 'div.title h1.content-head__title'

- 5 - 'div.content-text p.content-text__container'

- 6 - 'tecnologia'

- 7 - 2

- 8 - 'https:'

- 9 - False

- 10 - r"u=([^&]+)"

A sequência corresponde à tabela:

- 1 É o nome do site ou portal.

- 2 É a URL de onde parte a busca. Nesse caso, é uma URL de pesquisa e o assunto buscado pode ser escolhido. Dependendo do site, essa busca pode ser realizada pelo Google, por exemplo, sendo impossível prever o resultado. Quando isso ocorre, pode ser passada uma página que contenha as ocorrências procuradas, seguindo o mesmo princípio da busca. Neste ponto, estamos buscando uma página que contenha uma lista de páginas com os assuntos buscados.

- 3 São os seletores CSS que contêm os links para as páginas alvo. 'div.widget--info__text-container' é uma div pai onde se encontram as tags 'a'. O rastreador obterá todas as ocorrências de 'a', que são os caminhos para as páginas de interesse.

- 4 Este seletor recupera o título da página alvo. É indicado ao crawler o seletor pai e o seletor alvo.

- 5 É o seletor onde o conteúdo se encontra. Neste ponto, muita "sujeira" é recuperada: parágrafos de anúncios e outros assuntos que não estão no escopo, mas fique tranquilo, a IA nos ajudará a resolver isso. É indicado ao crawler o seletor pai e o seletor alvo.

- 6 Quando a página de busca é personalizada pelo site, você pode escolher um assunto, desde que ele exista no conteúdo, é claro, para que o rastreador direcione a busca corretamente. Se o site possuir um buscador do tipo Google, essa parte pode ser omitida e a página de assunto pode ser definida manualmente no item 2.

- 7 Define a quantidade de páginas alvo que serão buscadas dentro da página de busca. Existe uma lógica no algoritmo que limita essa busca. Logo, a quantidade de buscas é limitada pelo máximo retornado pelo site, caso você desconheça a quantidade retornada.

- 8 Alguns sites disponibilizam apenas os caminhos relativos ao gerar suas buscas, o que é comum. Você deve verificar o tipo de retorno e, se necessário, adicionar a URL necessária para o rastreador continuar a recuperação. Este complemento, se usado, virá sempre antes do caminho relativo, geralmente sendo o endereço do site. Sempre verifique essa parte com cuidado, pois se não for retornado um link válido, o algoritmo não trará resultados.

- 9 Use True se o caminho for absoluto e False se for usar o complemento.

- 10 Este é um caso especial onde o site retorna um link que engana seu robô. O link se parece com isso: https://g1.globo.com/busca/click?q=tecnologia&p=1&r=1724522800067&u=https%3A%2F%2Fgloboplay.globo.com%2Fv%2F12847167%2F&syn=False&key=f21f2df7300adb7400db720232211585. Este link retorna um conteúdo inútil, mas nele existe o link absoluto, que pode ser extraído e usado para acessar a página alvo. Aqui, é usada uma expressão regular que captura esta parte: u=https%3A%2F%2Fgloboplay.globo.com%2Fv%2F12847167%2F, e um parse do urllib converte este padrão em um padrão ASCII. Este regex deve ser usado somente em casos semelhantes e deve ser adequado ao caso de uso.

- Após a parte do rastreador fazer seu trabalho, é necessário tratar esses dados. Em outros tempos, esse trabalho poderia ser pesado. Imagine tentar resumir um texto usando algoritmos? Mas, felizmente, hoje temos as IA's, que são ferramentas incríveis para esse tipo de problema. O texto recuperado não vem muito limpo; está repleto de quebras de linha, emojis e outros caracteres indesejáveis. Nesse projeto, usei o Gemini do Google, o engine "gemini-1.5-flash", primeiro por ter uma API muito simples e, segundo, por ser gratuito. Claro que é bem restritivo, mas para este projeto serve muito bem.

- O próximo passo é a entrada de dados na IA e o prompt. O prompt que estou usando neste momento está embutido no código, e deixarei ele para eventuais consultas. Ele deve ser bem claro e detalhado. Neste caso, para saída de dados, estou usando a própria saída da IA diretamente. Eu pensei que isso poderia ser um problema; afinal, confiar uma saída de dados a uma IA generativa me parece uma ideia arriscada, mas durante o desenvolvimento, que durou 5 dias, ela sempre retornou o que eu pedi, e o programa nunca falhou por isso. Entretanto, posteriormente implementarei um verificador para isso. Ela retorna uma lista de dicionários, mas em formato str, o que não serve para nada. Então, usei um recurso interessante do Python, o ast.literal_eval() da lib ast, que identifica a estrutura de dados na string e a converte para uma estrutura de dados válida. Isso é tão útil que dá vontade de chorar de alegria.

- A saída de dados é concluída em pipe_line_9, na classe Bot, no método run(). A partir desse ponto, as particularidades são relativas ao aplicativo em que integrei o bot, e não vou especificá-las aqui.

- O resultado pode ser acessado no meu [Portfólio](https://www.brainstormtech.com.br/), na seção Artigos.
