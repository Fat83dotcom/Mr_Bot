import re
import os
import ast
from datetime import datetime
import urllib
import requests
from time import time
from bs4 import BeautifulSoup
from random import randint, seed
import google.generativeai as genai
from automation_db import DBConnection
from typing import Any


class Log:
    def register_log(self, path: str, payload: str):
        with open(path, 'a+', encoding='utf-8') as file:
            file.write(f'{payload} - Data/Hora: {datetime.now()}\n')


class Message():
    log = Log()

    @classmethod
    def send_message(self, message: str, method: str, class_) -> str:
        mess: str = f'''
            Error: {message} \n
            Method: {method} \n
            Class: {class_} \n
        '''
        self.log.register_log('/search_app_logs/log_error.txt', mess)


class Content:
    def __init__(
        self, title: str, article_content: str, origin_link: str, id_=-1
    ) -> None:
        self.id = id_
        self.title = title
        self.article_content = article_content
        self.origin_link = origin_link

    def __iter__(self):
        return (
            i for i in (
                self.id, self.title, self.article_content, self.origin_link
            )
        )


class WebSite:
    def __init__(
        self, site_name: str, search_url: str, search_result_selector: str,
        title_selector: str, content_selector: str, topic: str, n_links: int,
        link_complement: str, is_absolute_url: bool, url_pattern: str
    ) -> None:
        self.site_name = site_name
        self.search_url = search_url
        self.search_result_selector = search_result_selector
        self.title_selector = title_selector
        self.content_selector = content_selector
        self.topic = topic
        self.n_links = n_links
        self.link_complement = link_complement
        self.is_absolute_url = is_absolute_url
        self.url_pattern = url_pattern

    def __iter__(self):
        return (
            i for i in (
                self.site_name, self.search_url,
                self.search_result_selector, self.title_selector,
                self.content_selector, self.topic, self.n_links,
                self.link_complement, self.is_absolute_url, self.url_pattern
            )
        )


class DataHandler:
    def insert_id(self, target_data: list) -> list:
        try:
            changed_data: list = []
            id_counter: int = 0
            for list_content in target_data:
                for content in list_content:
                    # content.update({'id': id_counter})
                    content.__dict__['id'] = id_counter
                    changed_data.append(content)
                    id_counter += 1
        except Exception as e:
            Message.send_message(e, 'insert_id', self.__class__)
        return changed_data

    def reinsert_link(
        self, content_with_link: list, content_from_ia: list
    ) -> list:
        try:
            result: list = []
            for content_a in content_with_link:
                for content_b in content_from_ia:
                    if content_a.id == content_b['id'] \
                            and content_b['article_content'] != '':
                        content_a.article_content = content_b['article_content']
                        result.append(content_a)
        except Exception as e:
            Message.send_message(e, 'reinsert_link', self.__class__)
        return result

    def prepare_content_for_ia(self, content: Content) -> list:
        try:
            chosen_keys: list = []
            for attrs in content:
                target: dict = {}
                if attrs.article_content != '':
                    target['article_content'] = attrs.article_content
                    target['id'] = attrs.id
                chosen_keys.append(target)
        except Exception as e:
            Message.send_message(
                e, 'prepare_content_for_ia', self.__class__
            )
        return chosen_keys

    def text_converter(self, text: str) -> Any:
        try:
            return ast.literal_eval(text)
        except Exception as e:
            Message.send_message(e, 'text_converter', self.__class__)


class IATextSummarizer:
    def __init__(self, ia_engine: str) -> None:
        try:
            genai.configure(api_key=os.getenv("API_KEY"))
            self.model = genai.GenerativeModel(ia_engine)
        except Exception as e:
            Message.send_message(e, '__init__', self.__class__)

    def summarize_text(self, prompt: str, text: str) -> str:
        '''O prompt deve instruir à IA como resumir a lista de dicionários
        que ela recebe. A IA deve devolver os dados na forma de dicionarios
        com a chave respectiva ao resumo. Isso deve ser bem especificado.'''
        try:
            response = self.model.generate_content(
                f"""{prompt} : {text}"""
            )
        except Exception as e:
            Message.send_message(e, 'summarize_text', self.__class__)
        return response.text


class HtmlGenerator:
    def generator(self, target: list) -> str:
        try:
            result: str = ''
            for content in target:
                result += f'''
<div class="exo-2-font">
<strong><b>{content.title}:</b></strong>
<p>{content.article_content}</p>
<a href="{content.origin_link}" target="_blank" rel="noopener noreferrer">Saiba mais...</a>
<hr>
</div>\n
'''
        except Exception as e:
            Message.send_message(e, 'generator', self.__class__)
        return result


class Crawler:
    def __get_page(self, url: str) -> BeautifulSoup | None:
        try:
            html = requests.get(url, allow_redirects=True)
        except Exception as e:
            return Message.send_message(e, '__get_page', self.__class__)
        return BeautifulSoup(html.text, 'html.parser')

    def __get_safe(self, bs: BeautifulSoup, selector: str) -> str:
        try:
            child = bs.select(selector)
            if child is not None and len(child) > 0:
                return child[0].get_text()
            return ''
        except Exception as e:
            Message.send_message(e, '__get_safe', self.__class__)

    def __get_from_attr(self, bs: BeautifulSoup, attr: str) -> list:
        try:
            return [
                content.get(attr) for content in bs
            ]
        except Exception:
            return []

    def __get_page_change_search_topic(self, site: WebSite):
        try:
            url = ''
            if site.topic == '':
                url = site.search_url
            else:
                url = site.search_url + site.topic
        except Exception as e:
            Message.send_message(
                e, '__get_page_change_search_topic', self.__class__
            )
        return self.__get_page(url)

    def __select_random_link(self, links: list, number_links: int) -> list:
        seed(time())
        try:
            lentgh = len(links)
            if lentgh < number_links:
                return [
                    links[randint(0, (lentgh - 1))] for _ in range(lentgh)
                ]
            return [
                links[randint(0, (lentgh - 1))] for _ in range(number_links)
            ]
        except Exception as e:
            Message.send_message(
                e, '__select_random_link', self.__class__
            )

    def __parse_unquote_url(self, url: str, site: WebSite) -> str:
        '''
        Extrai parte de uma url com uma expressão regular e decodifica essa
        parte. É usada quando houver urls anti-robos, passando uma regex para
        Website.
        '''
        try:
            if site.url_pattern != '':
                pattern = fr"{site.url_pattern}"
                match = re.search(pattern, url)
                if not match:
                    return url
                return urllib.parse.unquote(match.group(1))
            return url
        except Exception as e:
            Message.send_message(
                e, '__parse_unquote_url', self.__class__
            )

    def __target_pages_engine(self, site: WebSite, target_url: str) -> Content:
        try:
            url = self.__parse_unquote_url(target_url, site)
            bs = self.__get_page(url)
            title = self.__get_safe(bs, site.title_selector)
            content = self.__get_safe(bs, site.content_selector)
        except Exception as e:
            Message.send_message(
                e, '__target_pages_engine', self.__class__
            )
        return Content(title, content, url)

    def __get_target_pages(
        self, site: WebSite, target_link: list
    ) -> list:
        result: list = []
        for link in target_link:
            try:
                url = ''
                if site.is_absolute_url:
                    url = link
                else:
                    url = site.link_complement + link
                result.append(self.__target_pages_engine(site, url))
            except Exception as e:
                Message.send_message(
                    e, '__get_target_pages', self.__class__
                )
        return result

    def search(self, site: WebSite) -> list[Content]:
        try:
            list_of_pages = self.__get_page_change_search_topic(site)
            target_links = list_of_pages.select(site.search_result_selector)
            links = self.__get_from_attr(target_links, 'href')
            select_links = self.__select_random_link(links, site.n_links)
        except Exception as e:
            Message.send_message(
                    e, 'search', self.__class__
                )
        return self.__get_target_pages(site, select_links)


class Post:
    seed(time())
    date = datetime.now()
    date_fmt = date.strftime('%d/%m/%y')

    def __init__(self, content: str) -> None:
        self.title: str = f'News Letter - {self.date_fmt}'
        self.excerpt: str = 'Notícias do dia selecionadas para você.'
        self.content = content
        self.createdAt: datetime = datetime.now()
        self.createdBy_id: int = 2
        self.categoryKey_id: int = 2
        self.slug: str = f'news-letter-{randint(1000, 1000000)}-bot'
        self.isPublished: bool = False


class Bot:
    def __init__(self) -> None:
        try:
            self.db = DBConnection()
            self.crawler = Crawler()
            self.d_handler = DataHandler()
            self.ia_engine = 'gemini-1.5-flash'
            self.ia_sumerizer = IATextSummarizer(self.ia_engine)
            self.gen_html = HtmlGenerator()
            self.log = Log()
            self.prompt = '''
        Faça um resumo do texto que está na chave "article_content", o
        resumo dever ter no máximo 2 parágrafos curtos e todos devem ter o
        mesmo tamanho, em média. Retire qualquer caractere que
        não seja letra e não retorne se a chave estiver
        vazia. Retorne o resultado da seguinte forma:
        [{"id": (respectivo número), "article_content":(respectivo resumo)}].
        As chaves devem ser separadas por virgulas para cada ocorrencia,
        exatamente como uma lista de dicionários Python. A saida deve ser
        exatamente assim.
        '''
        except Exception:
            ...

    def run(self) -> None:
        try:
            # Main PipeLine

            # Busca os dados dos sites no banco de dados
            pipe_line_1 = self.db.get_sites_metadata('register_sites')

            # cria as instancias de WebSite
            pipe_line_2: list = [
                WebSite(
                    row.site_name, row.search_url, row.search_result_selector,
                    row.title_selector, row.content_selector, row.topic,
                    row.n_links, row.link_complement, row.is_absolute_url,
                    row.url_pattern
                ) for row in pipe_line_1
            ]

            # busca os dados atraves das instancias WebSite
            pipe_line_3: list = [self.crawler.search(s) for s in pipe_line_2]

            # insere um identificador para sincronização posterior dos dados
            pipe_line_4 = self.d_handler.insert_id(pipe_line_3)

            # separa o texto e o id preparando para o processo de IA
            pipe_line_5 = self.d_handler.prepare_content_for_ia(
                pipe_line_4
            )

            # Dados passam pela IA para resumo dos textos
            pipe_line_6 = self.ia_sumerizer.summarize_text(
                self.prompt, str(pipe_line_5)
            )

            # Dados recebidos da IA são convertidos em carga util
            pipe_line_7 = self.d_handler.text_converter(pipe_line_6)

            # Reinserir os links em seus respectivos lugares
            pipe_line_8 = self.d_handler.reinsert_link(
                pipe_line_4, pipe_line_7
            )

            # Formatar os dados no formato HTML para serem inseridos
            pipe_line_9 = self.gen_html.generator(pipe_line_8)

            #  Inserir os dados, como um post no blog. Fim do ALgoritmo
            content = Post(pipe_line_9).__dict__

            self.db.insert_table('post', content)
        except Exception as e:
            self.log.register_log(
                '/search_app_logs/log_1.txt',
                e
            )


if __name__ == '__main__':
    main = Bot()
    main.run()

