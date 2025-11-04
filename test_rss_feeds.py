#!/usr/bin/env python3
"""
RSS Feed Testing Script
Tests all proposed RSS feeds for reliability, content quality, and geographic relevance.
Only sources that pass ALL tests will be recommended for production.
"""

import requests
import feedparser
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import json
import re
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Keywords to check for relevance
RELEVANCE_KEYWORDS = [
    'energy', 'oil', 'gas', 'renewable', 'solar', 'wind', 'nuclear', 'coal',
    'artificial intelligence', 'ai', 'machine learning', 'blockchain', 'cryptocurrency',
    'bitcoin', 'ethereum', 'fintech', 'technology', 'innovation'
]

# Geographic keywords for target regions
AFRICA_KEYWORDS = ['africa', 'african', 'nigeria', 'south africa', 'kenya', 'egypt', 'morocco', 'ghana', 'ethiopia']
LATAM_KEYWORDS = ['latin america', 'brazil', 'mexico', 'argentina', 'chile', 'colombia', 'peru', 'venezuela', 'uruguay']
MENA_KEYWORDS = ['middle east', 'gulf', 'saudi', 'uae', 'qatar', 'kuwait', 'bahrain', 'oman', 'jordan', 'lebanon', 'israel', 'palestine']

class RSSTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def test_rss_feed(self, name, url, region, language='English'):
        """Test a single RSS feed comprehensively"""
        logger.info(f"Testing RSS feed: {name} ({region})")
        
        result = {
            'name': name,
            'url': url,
            'region': region,
            'language': language,
            'status': 'FAILED',
            'tests_passed': 0,
            'total_tests': 6,
            'errors': [],
            'article_count': 0,
            'recent_articles': 0,
            'relevant_articles': 0,
            'geographic_articles': 0,
            'response_time': 0,
            'last_updated': None
        }
        
        try:
            # Test 1: Accessibility
            start_time = time.time()
            response = self.session.get(url, timeout=10)
            result['response_time'] = time.time() - start_time
            
            if response.status_code != 200:
                result['errors'].append(f"HTTP {response.status_code}")
                return result
                
            # Test 2: Valid XML/RSS Format
            try:
                feed = feedparser.parse(response.content)
                if not feed.entries:
                    result['errors'].append("No entries found in feed")
                    return result
            except Exception as e:
                result['errors'].append(f"Invalid RSS format: {str(e)}")
                return result
                
            result['tests_passed'] += 2
            
            # Test 3: Recent Articles (within 7 days)
            recent_count = 0
            for entry in feed.entries[:10]:  # Check first 10 entries
                if self.is_recent_article(entry):
                    recent_count += 1
                    
            if recent_count == 0:
                result['errors'].append("No recent articles found")
                return result
                
            result['recent_articles'] = recent_count
            result['tests_passed'] += 1
            
            # Test 4: Content Quality
            article_count = len(feed.entries)
            result['article_count'] = article_count
            
            if article_count < 5:
                result['errors'].append(f"Too few articles: {article_count}")
                return result
                
            result['tests_passed'] += 1
            
            # Test 5: Relevance to our keywords
            relevant_count = 0
            for entry in feed.entries[:20]:  # Check first 20 entries
                if self.is_relevant_article(entry):
                    relevant_count += 1
                    
            result['relevant_articles'] = relevant_count
            if relevant_count == 0:
                result['errors'].append("No relevant articles found")
                return result
                
            result['tests_passed'] += 1
            
            # Test 6: Geographic Relevance
            geographic_count = 0
            for entry in feed.entries[:20]:
                if self.is_geographically_relevant(entry, region):
                    geographic_count += 1
                    
            result['geographic_articles'] = geographic_count
            if geographic_count == 0:
                result['errors'].append(f"No {region} relevant articles found")
                return result
                
            result['tests_passed'] += 1
            
            # Check last updated
            if hasattr(feed.feed, 'updated'):
                result['last_updated'] = feed.feed.updated
                
            # All tests passed
            result['status'] = 'PASSED'
            logger.info(f"✅ {name} - All tests passed")
            
        except requests.exceptions.RequestException as e:
            result['errors'].append(f"Request failed: {str(e)}")
        except Exception as e:
            result['errors'].append(f"Unexpected error: {str(e)}")
            
        return result
        
    def is_recent_article(self, entry):
        """Check if article is from last 7 days"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])
                return pub_date > datetime.now() - timedelta(days=7)
            return False
        except:
            return False
            
    def is_relevant_article(self, entry):
        """Check if article contains relevant keywords"""
        text = ""
        if hasattr(entry, 'title'):
            text += entry.title.lower()
        if hasattr(entry, 'summary'):
            text += entry.summary.lower()
        if hasattr(entry, 'description'):
            text += entry.description.lower()
            
        return any(keyword in text for keyword in RELEVANCE_KEYWORDS)
        
    def is_geographically_relevant(self, entry, region):
        """Check if article is geographically relevant"""
        text = ""
        if hasattr(entry, 'title'):
            text += entry.title.lower()
        if hasattr(entry, 'summary'):
            text += entry.summary.lower()
        if hasattr(entry, 'description'):
            text += entry.description.lower()
            
        if region == 'Africa':
            return any(keyword in text for keyword in AFRICA_KEYWORDS)
        elif region == 'Latin America':
            return any(keyword in text for keyword in LATAM_KEYWORDS)
        elif region == 'MENA':
            return any(keyword in text for keyword in MENA_KEYWORDS)
        return True  # For general sources
        
    def test_all_feeds(self):
        """Test all proposed RSS feeds"""
        feeds_to_test = [
            # Africa - Nigeria
            ("Premium Times Nigeria", "https://www.premiumtimesng.com/rss", "Africa"),
            ("Vanguard Nigeria", "https://www.vanguardngr.com/rss", "Africa"),
            ("Punch Nigeria", "https://punchng.com/rss", "Africa"),
            ("This Day Nigeria", "https://www.thisdaylive.com/rss", "Africa"),
            ("The Guardian Nigeria", "https://guardian.ng/rss", "Africa"),
            ("Business Day Nigeria", "https://businessday.ng/rss", "Africa"),
            ("The Nation Nigeria", "https://thenationonlineng.net/rss", "Africa"),
            
            # Africa - South Africa
            ("News24 South Africa", "https://www.news24.com/rss", "Africa"),
            ("Mail & Guardian", "https://mg.co.za/rss", "Africa"),
            ("City Press", "https://www.news24.com/citypress/rss", "Africa"),
            ("Sowetan", "https://www.sowetanlive.co.za/rss", "Africa"),
            ("The Star", "https://www.iol.co.za/the-star/rss", "Africa"),
            ("Cape Times", "https://www.iol.co.za/cape-times/rss", "Africa"),
            ("The Citizen", "https://www.citizen.co.za/rss", "Africa"),
            ("Sunday Times", "https://www.timeslive.co.za/sunday-times/rss", "Africa"),
            ("The Times", "https://www.timeslive.co.za/the-times/rss", "Africa"),
            ("Business Report", "https://www.iol.co.za/business-report/rss", "Africa"),
            ("Fin24", "https://www.fin24.com/rss", "Africa"),
            ("Moneyweb", "https://www.moneyweb.co.za/rss", "Africa"),
            
            # Africa - Kenya
            ("The Standard Kenya", "https://www.standardmedia.co.ke/rss", "Africa"),
            ("Nation Kenya", "https://www.nation.co.ke/rss", "Africa"),
            ("Business Daily Kenya", "https://www.businessdailyafrica.com/rss", "Africa"),
            ("The Star Kenya", "https://www.the-star.co.ke/rss", "Africa"),
            ("Daily Nation Kenya", "https://www.nation.co.ke/rss", "Africa"),
            ("Capital FM Kenya", "https://www.capitalfm.co.ke/rss", "Africa"),
            ("KBC Kenya", "https://www.kbc.co.ke/rss", "Africa"),
            
            # Africa - Egypt
            ("Al Ahram Egypt", "https://english.ahram.org.eg/rss", "Africa"),
            ("Egypt Today", "https://www.egypttoday.com/rss", "Africa"),
            ("Daily News Egypt", "https://dailynewsegypt.com/rss", "Africa"),
            ("Egypt Independent", "https://www.egyptindependent.com/rss", "Africa"),
            ("Al Masry Al Youm", "https://www.almasryalyoum.com/rss", "Africa"),
            
            # Africa - Morocco
            ("Morocco World News", "https://www.moroccoworldnews.com/rss", "Africa"),
            ("Hespress Morocco", "https://www.hespress.com/rss", "Africa"),
            ("Le Matin Morocco", "https://lematin.ma/rss", "Africa"),
            ("L'Economiste Morocco", "https://www.leconomiste.com/rss", "Africa"),
            
            # Africa - Ghana
            ("Ghana Web", "https://www.ghanaweb.com/rss", "Africa"),
            ("Graphic Ghana", "https://www.graphic.com.gh/rss", "Africa"),
            ("Daily Graphic", "https://www.graphic.com.gh/rss", "Africa"),
            ("Modern Ghana", "https://www.modernghana.com/rss", "Africa"),
            ("Citi FM Ghana", "https://citifmonline.com/rss", "Africa"),
            ("Joy News Ghana", "https://www.myjoyonline.com/rss", "Africa"),
            
            # Africa - Ethiopia
            ("Addis Fortune Ethiopia", "https://addisfortune.net/rss", "Africa"),
            ("The Reporter Ethiopia", "https://www.thereporterethiopia.com/rss", "Africa"),
            ("Capital Ethiopia", "https://www.capitalethiopia.com/rss", "Africa"),
            ("Walta Information Center", "https://www.waltainfo.com/rss", "Africa"),
            ("Fana Broadcasting", "https://www.fanabc.com/rss", "Africa"),
            
            # Africa - Tanzania
            ("The Citizen Tanzania", "https://www.thecitizen.co.tz/rss", "Africa"),
            ("Daily News Tanzania", "https://dailynews.co.tz/rss", "Africa"),
            ("The Guardian Tanzania", "https://www.ippmedia.com/rss", "Africa"),
            ("Mwananchi Tanzania", "https://www.mwananchi.co.tz/rss", "Africa"),
            
            # Africa - Uganda
            ("New Vision Uganda", "https://www.newvision.co.ug/rss", "Africa"),
            ("Daily Monitor Uganda", "https://www.monitor.co.ug/rss", "Africa"),
            ("The Observer Uganda", "https://observer.ug/rss", "Africa"),
            ("Independent Uganda", "https://www.independent.co.ug/rss", "Africa"),
            
            # Africa - Zimbabwe
            ("The Herald Zimbabwe", "https://www.herald.co.zw/rss", "Africa"),
            ("NewsDay Zimbabwe", "https://www.newsday.co.zw/rss", "Africa"),
            ("The Standard Zimbabwe", "https://www.thestandard.co.zw/rss", "Africa"),
            ("Chronicle Zimbabwe", "https://www.chronicle.co.zw/rss", "Africa"),
            
            # Africa - Zambia
            ("The Post Zambia", "https://www.postzambia.com/rss", "Africa"),
            ("Times of Zambia", "https://www.times.co.zm/rss", "Africa"),
            ("Zambia Daily Mail", "https://www.daily-mail.co.zm/rss", "Africa"),
            
            # Africa - Botswana
            ("Mmegi Botswana", "https://www.mmegi.bw/rss", "Africa"),
            ("Botswana Guardian", "https://www.botswanaguardian.co.bw/rss", "Africa"),
            
            # Africa - Namibia
            ("The Namibian", "https://www.namibian.com.na/rss", "Africa"),
            ("New Era Namibia", "https://www.newera.com.na/rss", "Africa"),
            
            # Africa - Senegal
            ("Le Soleil Senegal", "https://lesoleil.sn/rss", "Africa"),
            ("Sud Quotidien Senegal", "https://www.sudonline.sn/rss", "Africa"),
            
            # Africa - Ivory Coast
            ("Fratmat Côte d'Ivoire", "https://www.fratmat.info/rss", "Africa"),
            ("Le Patriote Côte d'Ivoire", "https://www.lepatriote.net/rss", "Africa"),
            
            # Africa - Mali
            ("L'Essor Mali", "https://www.essor.ml/rss", "Africa"),
            
            # Africa - Burkina Faso
            ("Le Pays Burkina Faso", "https://lepays.bf/rss", "Africa"),
            
            # Africa - Niger
            ("Le Sahel Niger", "https://www.lesahel.org/rss", "Africa"),
            
            # Africa - Chad
            ("Le Progrès Chad", "https://www.leprogres.net/rss", "Africa"),
            
            # Africa - Cameroon
            ("Cameroon Tribune", "https://www.cameroon-tribune.cm/rss", "Africa"),
            ("The Post Cameroon", "https://www.postnewsline.com/rss", "Africa"),
            ("Le Messager Cameroon", "https://www.lemessager.net/rss", "Africa"),
            
            # Africa - Central African Republic
            ("La Nouvelle République Central African Republic", "https://www.lanouvellecentrafrique.info/rss", "Africa"),
            
            # Africa - DRC
            ("Le Potentiel DRC", "https://www.lepotentiel.cd/rss", "Africa"),
            ("La Libre Afrique DRC", "https://www.lalibreafrique.cd/rss", "Africa"),
            ("Le Phare DRC", "https://www.lephare.net/rss", "Africa"),
            
            # Africa - Congo
            ("La Semaine Africaine Congo", "https://www.lasemaineafricaine.net/rss", "Africa"),
            
            # Africa - Gabon
            ("Gabon Review", "https://www.gabonreview.com/rss", "Africa"),
            ("L'Union Gabon", "https://www.union.sn/rss", "Africa"),
            
            # Africa - Equatorial Guinea
            ("Guinée Conakry Info", "https://www.guineeconakry.info/rss", "Africa"),
            ("Guinée Matin", "https://www.guineematin.com/rss", "Africa"),
            
            # Africa - Guinea-Bissau
            ("Guinée Bissau", "https://www.guineebissau.net/rss", "Africa"),
            
            # Africa - Gambia
            ("The Point Gambia", "https://thepoint.gm/rss", "Africa"),
            
            # Africa - Cape Verde
            ("A Semana Cape Verde", "https://www.asemana.publ.cv/rss", "Africa"),
            ("Expresso das Ilhas Cape Verde", "https://expressodasilhas.cv/rss", "Africa"),
            
            # Africa - São Tomé and Príncipe
            ("STP Digital São Tomé", "https://www.stpdigital.net/rss", "Africa"),
            
            # Africa - Angola
            ("Jornal de Angola", "https://jornaldeangola.sapo.ao/rss", "Africa"),
            ("O País Angola", "https://opais.co.ao/rss", "Africa"),
            ("Notícias Angola", "https://www.noticiasdeangola.com/rss", "Africa"),
            
            # Africa - Mozambique
            ("O País Mozambique", "https://opais.co.mz/rss", "Africa"),
            ("Notícias Mozambique", "https://www.noticias.co.mz/rss", "Africa"),
            ("A Verdade Mozambique", "https://www.averdade.org.mz/rss", "Africa"),
            
            # Africa - Madagascar
            ("L'Express Madagascar", "https://www.lexpress.mg/rss", "Africa"),
            ("Madagascar Tribune", "https://www.madagascar-tribune.com/rss", "Africa"),
            ("Midi Madagasikara", "https://www.midi-madagasikara.mg/rss", "Africa"),
            
            # Africa - Mauritius
            ("L'Express Maurice", "https://www.lexpress.mu/rss", "Africa"),
            ("Le Mauricien", "https://www.lemauricien.com/rss", "Africa"),
            
            # Africa - Seychelles
            ("Seychelles Nation", "https://www.nation.sc/rss", "Africa"),
            
            # Africa - Comoros
            ("Al-Watwan Comoros", "https://www.alwatwan.net/rss", "Africa"),
            
            # Africa - Djibouti
            ("La Nation Djibouti", "https://www.lanation.dj/rss", "Africa"),
            
            # Africa - Somalia
            ("Somali National News Agency", "https://www.sonna.so/rss", "Africa"),
            ("Hiiraan Online Somalia", "https://www.hiiraan.com/rss", "Africa"),
            ("Garowe Online Somalia", "https://www.garoweonline.com/rss", "Africa"),
            
            # Africa - Eritrea
            ("Eritrea Profile", "https://www.eritrea-profile.net/rss", "Africa"),
            
            # Africa - Sudan
            ("Sudan Tribune", "https://www.sudantribune.com/rss", "Africa"),
            ("Radio Dabanga Sudan", "https://www.dabangasudan.org/rss", "Africa"),
            
            # Africa - South Sudan
            ("South Sudan News Agency", "https://www.southsudannewsagency.com/rss", "Africa"),
            ("Eye Radio South Sudan", "https://eyeradio.org/rss", "Africa"),
            
            # Africa - Libya
            ("Libya Herald", "https://www.libyaherald.com/rss", "Africa"),
            ("Libya Observer", "https://www.libyaobserver.ly/rss", "Africa"),
            
            # Africa - Tunisia
            ("Tunis Afrique Presse", "https://www.tap.info.tn/rss", "Africa"),
            ("La Presse Tunisia", "https://www.lapresse.tn/rss", "Africa"),
            ("Le Temps Tunisia", "https://www.letemps.com.tn/rss", "Africa"),
            
            # Africa - Algeria
            ("El Watan Algeria", "https://www.elwatan.com/rss", "Africa"),
            ("Liberté Algeria", "https://www.liberte-algerie.com/rss", "Africa"),
            ("El Moudjahid Algeria", "https://www.elmoudjahid.com/rss", "Africa"),
            ("Le Quotidien d'Oran Algeria", "https://www.lequotidien-oran.com/rss", "Africa"),
            ("La Tribune Algérienne", "https://www.latribune-online.com/rss", "Africa"),
            ("Le Matin d'Algérie", "https://www.lematindz.net/rss", "Africa"),
            ("L'Expression Algeria", "https://www.lexpressiondz.com/rss", "Africa"),
            ("Le Soir d'Algérie", "https://www.lesoirdalgerie.com/rss", "Africa"),
            ("Le Jeune Indépendant Algeria", "https://www.lejeune-independant.com/rss", "Africa"),
            ("Le Courrier d'Algérie", "https://www.lecourrier-dalgerie.com/rss", "Africa"),
            ("Le Temps d'Algérie", "https://www.letemps-dz.com/rss", "Africa"),
            ("Le Buteur Algeria", "https://www.lebuteur.com/rss", "Africa"),
            ("Le Financier Algeria", "https://www.lefinancier-dz.com/rss", "Africa"),
            ("Le Maghreb Algeria", "https://www.lemaghreb-dz.com/rss", "Africa"),
            ("Le Quotidien d'Algérie", "https://www.lequotidien-algerie.org/rss", "Africa"),
            
            # Latin America - Brazil
            ("Folha de S.Paulo Energia", "https://feeds.folha.uol.com.br/folha/energia/rss091.xml", "Latin America"),
            ("Folha de S.Paulo Economia", "https://feeds.folha.uol.com.br/folha/economia/rss091.xml", "Latin America"),
            ("Folha de S.Paulo Mercado", "https://feeds.folha.uol.com.br/folha/mercado/rss091.xml", "Latin America"),
            ("O Globo Brasil", "https://oglobo.globo.com/rss.xml", "Latin America"),
            ("O Estado de S.Paulo", "https://www.estadao.com.br/rss", "Latin America"),
            ("Jornal do Brasil", "https://www.jb.com.br/rss", "Latin America"),
            ("Correio Braziliense", "https://www.correiobraziliense.com.br/rss", "Latin America"),
            ("Zero Hora", "https://gauchazh.clicrbs.com.br/rss", "Latin America"),
            ("Gazeta do Povo", "https://www.gazetadopovo.com.br/rss", "Latin America"),
            ("Valor Econômico", "https://www.valor.com.br/rss", "Latin America"),
            ("Exame Brasil", "https://exame.com/rss", "Latin America"),
            ("IstoÉ Dinheiro", "https://www.istoedinheiro.com.br/rss", "Latin America"),
            ("Época Negócios", "https://epocanegocios.globo.com/rss", "Latin America"),
            ("InfoMoney", "https://www.infomoney.com.br/rss", "Latin America"),
            ("Money Report", "https://www.moneyreport.com.br/rss", "Latin America"),
            ("Investimentos e Notícias", "https://www.investimentosenoticias.com.br/rss", "Latin America"),
            
            # Latin America - Mexico
            ("El Universal México", "https://www.eluniversal.com.mx/rss/", "Latin America"),
            ("El Universal México Economía", "https://www.eluniversal.com.mx/economia/rss", "Latin America"),
            ("Reforma México", "https://www.reforma.com/rss", "Latin America"),
            ("La Jornada México", "https://www.jornada.com.mx/rss", "Latin America"),
            ("Excélsior México", "https://www.excelsior.com.mx/rss", "Latin America"),
            ("Milenio México", "https://www.milenio.com/rss", "Latin America"),
            ("El Financiero México", "https://www.elfinanciero.com.mx/rss", "Latin America"),
            ("El Economista México", "https://www.eleconomista.com.mx/rss", "Latin America"),
            ("Expansión México", "https://expansion.mx/rss", "Latin America"),
            
            # Latin America - Argentina
            ("La Nación Argentina", "https://www.lanacion.com.ar/rss/energia", "Latin America"),
            ("La Nación Argentina Economía", "https://www.lanacion.com.ar/rss/economia", "Latin America"),
            ("Clarín Argentina", "https://www.clarin.com/rss", "Latin America"),
            ("Página/12 Argentina", "https://www.pagina12.com.ar/rss", "Latin America"),
            ("La Voz del Interior", "https://www.lavoz.com.ar/rss", "Latin America"),
            ("El Cronista Argentina", "https://www.cronista.com/rss", "Latin America"),
            ("Ámbito Financiero Argentina", "https://www.ambito.com/rss", "Latin America"),
            
            # Latin America - Chile
            ("El Mercurio Chile", "https://www.elmercurio.com/rss/", "Latin America"),
            ("La Tercera Chile", "https://www.latercera.com/rss", "Latin America"),
            ("El Mostrador Chile", "https://www.elmostrador.cl/rss", "Latin America"),
            ("La Segunda Chile", "https://www.lasegunda.com/rss", "Latin America"),
            
            # Latin America - Colombia
            ("El Tiempo Colombia", "https://www.eltiempo.com/rss/", "Latin America"),
            ("El Espectador Colombia", "https://www.elespectador.com/rss", "Latin America"),
            ("El Colombiano", "https://www.elcolombiano.com/rss", "Latin America"),
            ("Portafolio Colombia", "https://www.portafolio.co/rss", "Latin America"),
            ("La República Colombia", "https://www.larepublica.co/rss", "Latin America"),
            
            # Latin America - Peru
            ("El Comercio Perú", "https://elcomercio.pe/rss/", "Latin America"),
            ("El Comercio Perú Economía", "https://elcomercio.pe/economia/rss/", "Latin America"),
            ("La República Perú", "https://larepublica.pe/rss", "Latin America"),
            ("Perú 21", "https://peru21.pe/rss", "Latin America"),
            ("Gestión Perú", "https://gestion.pe/rss", "Latin America"),
            ("El Peruano", "https://www.elperuano.pe/rss", "Latin America"),
            ("Correo Perú", "https://diariocorreo.pe/rss", "Latin America"),
            ("Trome Perú", "https://trome.pe/rss", "Latin America"),
            ("Ojo Perú", "https://ojo.pe/rss", "Latin America"),
            
            # Latin America - Venezuela
            ("El Nacional Venezuela", "https://www.el-nacional.com/rss", "Latin America"),
            ("El Universal Venezuela", "https://www.eluniversal.com/rss", "Latin America"),
            ("Últimas Noticias Venezuela", "https://www.ultimasnoticias.com.ve/rss", "Latin America"),
            ("El Tiempo Venezuela", "https://www.eltiempo.com.ve/rss", "Latin America"),
            ("El Mundo Venezuela", "https://www.elmundo.com.ve/rss", "Latin America"),
            ("El Impulso Venezuela", "https://www.elimpulso.com/rss", "Latin America"),
            ("El Carabobeño Venezuela", "https://www.elcarabobeño.com/rss", "Latin America"),
            ("El Diario de Caracas", "https://www.eldiario.com/rss", "Latin America"),
            ("El Nuevo País Venezuela", "https://www.elnuevopais.com/rss", "Latin America"),
            
            # Latin America - Ecuador
            ("El Comercio Ecuador", "https://www.elcomercio.com/rss", "Latin America"),
            ("El Universo Ecuador", "https://www.eluniverso.com/rss", "Latin America"),
            ("La Hora Ecuador", "https://www.lahora.com.ec/rss", "Latin America"),
            ("El Telégrafo Ecuador", "https://www.eltelegrafo.com.ec/rss", "Latin America"),
            ("El Mercurio Ecuador", "https://www.elmercurio.com.ec/rss", "Latin America"),
            ("El Diario Ecuador", "https://www.eldiario.ec/rss", "Latin America"),
            ("El Tiempo Ecuador", "https://www.eltiempo.com.ec/rss", "Latin America"),
            
            # Latin America - Bolivia
            ("La Razón Bolivia", "https://www.la-razon.com/rss", "Latin America"),
            ("El Deber Bolivia", "https://www.eldeber.com.bo/rss", "Latin America"),
            ("Los Tiempos Bolivia", "https://www.lostiempos.com/rss", "Latin America"),
            ("El Diario Bolivia", "https://www.eldiario.net/rss", "Latin America"),
            ("La Prensa Bolivia", "https://www.laprensa.com.bo/rss", "Latin America"),
            ("El País Bolivia", "https://www.elpais.com.bo/rss", "Latin America"),
            ("El Mundo Bolivia", "https://www.elmundo.com.bo/rss", "Latin America"),
            ("El Sol Bolivia", "https://www.elsol.com.bo/rss", "Latin America"),
            
            # Latin America - Paraguay
            ("ABC Color Paraguay", "https://www.abc.com.py/rss", "Latin America"),
            ("Última Hora Paraguay", "https://www.ultimahora.com/rss", "Latin America"),
            ("La Nación Paraguay", "https://www.lanacion.com.py/rss", "Latin America"),
            ("El Diario Paraguay", "https://www.eldiario.com.py/rss", "Latin America"),
            ("Hoy Paraguay", "https://www.hoy.com.py/rss", "Latin America"),
            ("El País Paraguay", "https://www.elpais.com.py/rss", "Latin America"),
            ("El Mundo Paraguay", "https://www.elmundo.com.py/rss", "Latin America"),
            ("El Sol Paraguay", "https://www.elsol.com.py/rss", "Latin America"),
            
            # Latin America - Uruguay
            ("El Observador Uruguay", "https://www.elobservador.com.uy/rss", "Latin America"),
            ("El País Uruguay", "https://www.elpais.com.uy/rss", "Latin America"),
            ("La República Uruguay", "https://www.larepublica.com.uy/rss", "Latin America"),
            ("El Diario Uruguay", "https://www.eldiario.com.uy/rss", "Latin America"),
            ("El Telégrafo Uruguay", "https://www.eltelegrafo.com.uy/rss", "Latin America"),
            ("El Mercurio Uruguay", "https://www.elmercurio.com.uy/rss", "Latin America"),
            ("El Tiempo Uruguay", "https://www.eltiempo.com.uy/rss", "Latin America"),
            ("El Mundo Uruguay", "https://www.elmundo.com.uy/rss", "Latin America"),
            ("El Sol Uruguay", "https://www.elsol.com.uy/rss", "Latin America"),
            
            # Latin America - Guyana
            ("El Nacional Guyana", "https://www.elnacional.com.gy/rss", "Latin America"),
            ("Stabroek News Guyana", "https://www.stabroeknews.com/rss", "Latin America"),
            ("Kaieteur News Guyana", "https://www.kaieteurnewsonline.com/rss", "Latin America"),
            ("Guyana Chronicle", "https://www.guyanachronicle.com/rss", "Latin America"),
            ("Demerara Waves Guyana", "https://www.demerarawaves.com/rss", "Latin America"),
            ("News Room Guyana", "https://www.newsroom.gy/rss", "Latin America"),
            
            # Latin America - Suriname
            ("El Nacional Suriname", "https://www.elnacional.com.sr/rss", "Latin America"),
            ("De Ware Tijd Suriname", "https://www.dwtonline.com/rss", "Latin America"),
            ("Suriname Herald", "https://www.surinameherald.com/rss", "Latin America"),
            ("Dagblad Suriname", "https://www.dagbladsuriname.com/rss", "Latin America"),
            ("Suriname Times", "https://www.surinametimes.com/rss", "Latin America"),
            ("Suriname News", "https://www.surinamenews.com/rss", "Latin America"),
            
            # Latin America - French Guiana
            ("France Guyane", "https://www.franceguyane.fr/rss", "Latin America"),
            ("La 1ère Guyane", "https://la1ere.francetvinfo.fr/guyane/rss", "Latin America"),
            ("Guyane la 1ère", "https://guyane.la1ere.fr/rss", "Latin America"),
            ("Le Journal de la Guyane", "https://www.lejournaldelaguyane.com/rss", "Latin America"),
            ("La Dépêche de la Guyane", "https://www.ladepecheguyane.com/rss", "Latin America"),
            ("Le Progrès Guyane", "https://www.leprogresguyane.com/rss", "Latin America"),
            ("Le Soir Guyane", "https://www.lesoirguyane.com/rss", "Latin America"),
            ("Le Matin Guyane", "https://www.lematinguyane.com/rss", "Latin America"),
            ("Le Temps Guyane", "https://www.letempsguyane.com/rss", "Latin America"),
            ("Le Buteur Guyane", "https://www.lebuteurguyane.com/rss", "Latin America"),
            ("Le Financier Guyane", "https://www.lefinancierguyane.com/rss", "Latin America"),
            ("Le Maghreb Guyane", "https://www.lemaghrebguyane.com/rss", "Latin America"),
            ("Le Quotidien Guyane", "https://www.lequotidienguyane.com/rss", "Latin America"),
            
            # MENA - Saudi Arabia
            ("Al Arabiya English", "https://english.alarabiya.net/rss.xml", "MENA"),
            ("Al Arabiya Business", "https://english.alarabiya.net/business/rss.xml", "MENA"),
            ("Al Arabiya Economy", "https://english.alarabiya.net/economy/rss.xml", "MENA"),
            ("Arab News", "https://www.arabnews.com/rss", "MENA"),
            ("Arab News Business", "https://www.arabnews.com/business/rss", "MENA"),
            ("Arab News Economy", "https://www.arabnews.com/economy/rss", "MENA"),
            ("Asharq Al-Awsat", "https://english.aawsat.com/rss", "MENA"),
            ("Asharq Al-Awsat Business", "https://english.aawsat.com/business/rss", "MENA"),
            ("Asharq Al-Awsat Economy", "https://english.aawsat.com/economy/rss", "MENA"),
            
            # MENA - UAE
            ("Gulf News", "https://gulfnews.com/rss", "MENA"),
            ("Gulf News Business", "https://gulfnews.com/business/rss", "MENA"),
            ("Gulf News Economy", "https://gulfnews.com/economy/rss", "MENA"),
            ("The National UAE", "https://www.thenational.ae/rss", "MENA"),
            ("The National UAE Business", "https://www.thenational.ae/business/rss", "MENA"),
            ("The National UAE Economy", "https://www.thenational.ae/economy/rss", "MENA"),
            
            # MENA - Qatar
            ("Al Jazeera English", "https://www.aljazeera.com/rss", "MENA"),
            ("Al Jazeera Business", "https://www.aljazeera.com/business/rss", "MENA"),
            ("Al Jazeera Economy", "https://www.aljazeera.com/economy/rss", "MENA"),
            
            # MENA - Kuwait
            ("Kuwait Times", "https://www.kuwaittimes.com/rss", "MENA"),
            ("Arab Times Kuwait", "https://www.arabtimesonline.com/rss", "MENA"),
            ("Kuwait News Agency", "https://www.kuna.net.kw/rss", "MENA"),
            
            # MENA - Bahrain
            ("Gulf Daily News", "https://www.gdnonline.com/rss", "MENA"),
            ("Bahrain News Agency", "https://www.bna.bh/rss", "MENA"),
            ("Al-Wasat Bahrain", "https://www.alwasatnews.com/rss", "MENA"),
            
            # MENA - Oman
            ("Times of Oman", "https://timesofoman.com/rss", "MENA"),
            ("Oman Observer", "https://www.omanobserver.om/rss", "MENA"),
            ("Oman News Agency", "https://www.omannews.gov.om/rss", "MENA"),
            
            # MENA - Yemen
            ("Yemen Times", "https://www.yementimes.com/rss", "MENA"),
            ("Yemen Observer", "https://www.yobserver.com/rss", "MENA"),
            ("Saba News Agency", "https://www.sabanews.net/rss", "MENA"),
            
            # MENA - Iraq
            ("Iraq Times", "https://www.iraqtimes.com/rss", "MENA"),
            ("Al-Sabah Iraq", "https://www.alsabah.com.iq/rss", "MENA"),
            ("Al-Mada Iraq", "https://www.almadapaper.net/rss", "MENA"),
            
            # MENA - Iran
            ("Tehran Times", "https://www.tehrantimes.com/rss", "MENA"),
            ("Iran Daily", "https://www.iran-daily.com/rss", "MENA"),
            ("Fars News Agency", "https://www.farsnews.ir/rss", "MENA"),
            
            # MENA - Syria
            ("Syria Times", "https://www.syriatimes.sy/rss", "MENA"),
            ("SANA Syria", "https://www.sana.sy/rss", "MENA"),
            ("Al-Watan Syria", "https://www.alwatan.sy/rss", "MENA"),
            
            # MENA - Lebanon
            ("The Daily Star Lebanon", "https://www.dailystar.com.lb/rss", "MENA"),
            ("An-Nahar Lebanon", "https://www.annahar.com/rss", "MENA"),
            ("Al-Akhbar Lebanon", "https://www.al-akhbar.com/rss", "MENA"),
            
            # MENA - Jordan
            ("Jordan Times", "https://www.jordantimes.com/rss", "MENA"),
            ("Al-Rai Jordan", "https://www.alrai.com/rss", "MENA"),
            ("Petra News Agency", "https://www.petra.gov.jo/rss", "MENA"),
            
            # MENA - Israel
            ("Jerusalem Post", "https://www.jpost.com/rss", "MENA"),
            ("Jerusalem Post Business", "https://www.jpost.com/business/rss", "MENA"),
            ("Jerusalem Post Economy", "https://www.jpost.com/economy/rss", "MENA"),
            ("Haaretz", "https://www.haaretz.com/rss", "MENA"),
            ("Haaretz Business", "https://www.haaretz.com/business/rss", "MENA"),
            ("Haaretz Economy", "https://www.haaretz.com/economy/rss", "MENA"),
            ("Times of Israel", "https://www.timesofisrael.com/rss", "MENA"),
            ("Ynet News", "https://www.ynetnews.com/rss", "MENA"),
            ("Israel Hayom", "https://www.israelhayom.co.il/rss", "MENA"),
            ("Maariv", "https://www.maariv.co.il/rss", "MENA"),
            ("Yedioth Ahronoth", "https://www.ynet.co.il/rss", "MENA"),
            
            # MENA - Palestine
            ("Palestine News Network", "https://www.pnn.ps/rss", "MENA"),
            ("WAFA News Agency", "https://www.wafa.ps/rss", "MENA"),
            ("Al-Quds", "https://www.alquds.com/rss", "MENA"),
            
            # MENA - Turkey
            ("Daily Sabah", "https://www.dailysabah.com/rss", "MENA"),
            ("Daily Sabah Business", "https://www.dailysabah.com/business/rss", "MENA"),
            ("Daily Sabah Economy", "https://www.dailysabah.com/economy/rss", "MENA"),
            ("Hurriyet Daily News", "https://www.hurriyetdailynews.com/rss", "MENA"),
            ("Hurriyet Daily News Business", "https://www.hurriyetdailynews.com/business/rss", "MENA"),
            ("Hurriyet Daily News Economy", "https://www.hurriyetdailynews.com/economy/rss", "MENA"),
            ("Today's Zaman", "https://www.todayszaman.com/rss", "MENA"),
            ("Today's Zaman Business", "https://www.todayszaman.com/business/rss", "MENA"),
            ("Today's Zaman Economy", "https://www.todayszaman.com/economy/rss", "MENA"),
            ("Zaman", "https://www.zaman.com.tr/rss", "MENA"),
            ("Zaman Business", "https://www.zaman.com.tr/business/rss", "MENA"),
            ("Zaman Economy", "https://www.zaman.com.tr/economy/rss", "MENA"),
            ("Milliyet", "https://www.milliyet.com.tr/rss", "MENA"),
            ("Milliyet Business", "https://www.milliyet.com.tr/business/rss", "MENA"),
            ("Milliyet Economy", "https://www.milliyet.com.tr/economy/rss", "MENA"),
            ("Sabah", "https://www.sabah.com.tr/rss", "MENA"),
            ("Sabah Business", "https://www.sabah.com.tr/business/rss", "MENA"),
            ("Sabah Economy", "https://www.sabah.com.tr/economy/rss", "MENA"),
            ("Yeni Şafak", "https://www.yenisafak.com/rss", "MENA"),
            ("Yeni Şafak Business", "https://www.yenisafak.com/business/rss", "MENA"),
            ("Yeni Şafak Economy", "https://www.yenisafak.com/economy/rss", "MENA"),
            ("Star", "https://www.star.com.tr/rss", "MENA"),
            ("Star Business", "https://www.star.com.tr/business/rss", "MENA"),
            ("Star Economy", "https://www.star.com.tr/economy/rss", "MENA"),
            ("Akşam", "https://www.aksam.com.tr/rss", "MENA"),
            ("Akşam Business", "https://www.aksam.com.tr/business/rss", "MENA"),
            ("Akşam Economy", "https://www.aksam.com.tr/economy/rss", "MENA"),
            ("Cumhuriyet", "https://www.cumhuriyet.com.tr/rss", "MENA"),
            ("Cumhuriyet Business", "https://www.cumhuriyet.com.tr/business/rss", "MENA"),
            ("Cumhuriyet Economy", "https://www.cumhuriyet.com.tr/economy/rss", "MENA"),
            ("Sözcü", "https://www.sozcu.com.tr/rss", "MENA"),
            ("Sözcü Business", "https://www.sozcu.com.tr/business/rss", "MENA"),
            ("Sözcü Economy", "https://www.sozcu.com.tr/economy/rss", "MENA"),
            ("Hürriyet", "https://www.hurriyet.com.tr/rss", "MENA"),
            ("Hürriyet Business", "https://www.hurriyet.com.tr/business/rss", "MENA"),
            ("Hürriyet Economy", "https://www.hurriyet.com.tr/economy/rss", "MENA"),
            ("Posta", "https://www.posta.com.tr/rss", "MENA"),
            ("Posta Business", "https://www.posta.com.tr/business/rss", "MENA"),
            ("Posta Economy", "https://www.posta.com.tr/economy/rss", "MENA"),
            ("Takvim", "https://www.takvim.com.tr/rss", "MENA"),
            ("Takvim Business", "https://www.takvim.com.tr/business/rss", "MENA"),
            ("Takvim Economy", "https://www.takvim.com.tr/economy/rss", "MENA"),
            ("Vatan", "https://www.gazetevatan.com/rss", "MENA"),
            ("Vatan Business", "https://www.gazetevatan.com/business/rss", "MENA"),
            ("Vatan Economy", "https://www.gazetevatan.com/economy/rss", "MENA"),
            ("Yeni Akit", "https://www.yeniakit.com.tr/rss", "MENA"),
            ("Yeni Akit Business", "https://www.yeniakit.com.tr/business/rss", "MENA"),
            ("Yeni Akit Economy", "https://www.yeniakit.com.tr/economy/rss", "MENA"),
            ("Yeni Çağ", "https://www.yenicag.com.tr/rss", "MENA"),
            ("Yeni Çağ Business", "https://www.yenicag.com.tr/business/rss", "MENA"),
            ("Yeni Çağ Economy", "https://www.yenicag.com.tr/economy/rss", "MENA"),
            ("Yeni Mesaj", "https://www.yenimesaj.com.tr/rss", "MENA"),
            ("Yeni Mesaj Business", "https://www.yenimesaj.com.tr/business/rss", "MENA"),
            ("Yeni Mesaj Economy", "https://www.yenimesaj.com.tr/economy/rss", "MENA"),
            ("Yeni Asır", "https://www.yeniasir.com.tr/rss", "MENA"),
            ("Yeni Asır Business", "https://www.yeniasir.com.tr/business/rss", "MENA"),
            ("Yeni Asır Economy", "https://www.yeniasir.com.tr/economy/rss", "MENA"),
            ("Yeni Asya", "https://www.yeniasya.com.tr/rss", "MENA"),
            ("Yeni Asya Business", "https://www.yeniasya.com.tr/business/rss", "MENA"),
            ("Yeni Asya Economy", "https://www.yeniasya.com.tr/economy/rss", "MENA"),
            ("Yeni Birlik", "https://www.yenibirlik.com.tr/rss", "MENA"),
            ("Yeni Birlik Business", "https://www.yenibirlik.com.tr/business/rss", "MENA"),
            ("Yeni Birlik Economy", "https://www.yenibirlik.com.tr/economy/rss", "MENA"),
            
            # MENA - Cyprus
            ("Cyprus Mail", "https://www.cyprus-mail.com/rss", "MENA"),
            ("Cyprus Times", "https://www.cyprustimes.com/rss", "MENA"),
            ("Cyprus News Agency", "https://www.cna.org.cy/rss", "MENA"),
            
            # MENA - Egypt
            ("Al Ahram Egypt", "https://english.ahram.org.eg/rss", "MENA"),
            ("Egypt Today", "https://www.egypttoday.com/rss", "MENA"),
            ("Daily News Egypt", "https://dailynewsegypt.com/rss", "MENA"),
            ("Egypt Independent", "https://www.egyptindependent.com/rss", "MENA"),
            ("Al Masry Al Youm", "https://www.almasryalyoum.com/rss", "MENA"),
            
            # MENA - Libya
            ("Libya Herald", "https://www.libyaherald.com/rss", "MENA"),
            ("Libya Observer", "https://www.libyaobserver.ly/rss", "MENA"),
            ("Libya News Agency", "https://www.lana.gov.ly/rss", "MENA"),
            
            # MENA - Tunisia
            ("Tunis Afrique Presse", "https://www.tap.info.tn/rss", "MENA"),
            ("La Presse Tunisia", "https://www.lapresse.tn/rss", "MENA"),
            ("Le Temps Tunisia", "https://www.letemps.com.tn/rss", "MENA"),
            ("Tunisie Numérique", "https://www.tunisienumerique.com/rss", "MENA"),
            
            # MENA - Algeria
            ("El Watan Algeria", "https://www.elwatan.com/rss", "MENA"),
            ("Liberté Algeria", "https://www.liberte-algerie.com/rss", "MENA"),
            ("El Moudjahid Algeria", "https://www.elmoudjahid.com/rss", "MENA"),
            ("Le Quotidien d'Oran Algeria", "https://www.lequotidien-oran.com/rss", "MENA"),
            ("La Tribune Algérienne", "https://www.latribune-online.com/rss", "MENA"),
            ("Le Matin d'Algérie", "https://www.lematindz.net/rss", "MENA"),
            ("L'Expression Algeria", "https://www.lexpressiondz.com/rss", "MENA"),
            ("Le Soir d'Algérie", "https://www.lesoirdalgerie.com/rss", "MENA"),
            ("Le Jeune Indépendant Algeria", "https://www.lejeune-independant.com/rss", "MENA"),
            ("Le Courrier d'Algérie", "https://www.lecourrier-dalgerie.com/rss", "MENA"),
            ("Le Temps d'Algérie", "https://www.letemps-dz.com/rss", "MENA"),
            ("Le Buteur Algeria", "https://www.lebuteur.com/rss", "MENA"),
            ("Le Financier Algeria", "https://www.lefinancier-dz.com/rss", "MENA"),
            ("Le Maghreb Algeria", "https://www.lemaghreb-dz.com/rss", "MENA"),
            ("Le Quotidien d'Algérie", "https://www.lequotidien-algerie.org/rss", "MENA"),
            
            # MENA - Morocco
            ("Morocco World News", "https://www.moroccoworldnews.com/rss", "MENA"),
            ("Hespress Morocco", "https://www.hespress.com/rss", "MENA"),
            ("Le Matin Morocco", "https://lematin.ma/rss", "MENA"),
            ("L'Economiste Morocco", "https://www.leconomiste.com/rss", "MENA"),
            ("Aujourd'hui le Maroc", "https://www.aujourdhui.ma/rss", "MENA"),
            ("Le Soir Échos Morocco", "https://www.lesoirechos.ma/rss", "MENA"),
            
            # MENA - Mauritania
            ("La Nouvelle République Mauritanie", "https://www.lanouvellemr.com/rss", "MENA"),
            ("Mauritanie Info", "https://www.mauritanie.info/rss", "MENA"),
            ("Mauritanie News", "https://www.mauritanienews.com/rss", "MENA"),
            
            # MENA - Western Sahara
            ("Sahara Press Service", "https://www.spsrasd.info/rss", "MENA"),
            ("La République Sahraouie", "https://www.larepubliquesahraouie.com/rss", "MENA"),
            ("Sahara News", "https://www.saharanews.com/rss", "MENA"),
            
            # MENA - Sudan
            ("Sudan Tribune", "https://www.sudantribune.com/rss", "MENA"),
            ("Radio Dabanga Sudan", "https://www.dabangasudan.org/rss", "MENA"),
            ("Sudan News Agency", "https://www.suna-sd.net/rss", "MENA"),
            
            # MENA - South Sudan
            ("South Sudan News Agency", "https://www.southsudannewsagency.com/rss", "MENA"),
            ("Eye Radio South Sudan", "https://eyeradio.org/rss", "MENA"),
            ("Juba Monitor", "https://www.jubamonitor.com/rss", "MENA"),
            
            # MENA - Ethiopia
            ("Addis Fortune Ethiopia", "https://addisfortune.net/rss", "MENA"),
            ("The Reporter Ethiopia", "https://www.thereporterethiopia.com/rss", "MENA"),
            ("Capital Ethiopia", "https://www.capitalethiopia.com/rss", "MENA"),
            ("Walta Information Center", "https://www.waltainfo.com/rss", "MENA"),
            ("Fana Broadcasting", "https://www.fanabc.com/rss", "MENA"),
            
            # MENA - Eritrea
            ("Eritrea Profile", "https://www.eritrea-profile.net/rss", "MENA"),
            ("Eritrea News", "https://www.eritrea-news.com/rss", "MENA"),
            ("Eritrea Information", "https://www.eritrea-info.com/rss", "MENA"),
            
            # MENA - Djibouti
            ("La Nation Djibouti", "https://www.lanation.dj/rss", "MENA"),
            ("Djibouti News", "https://www.djibouti-news.com/rss", "MENA"),
            ("Djibouti Info", "https://www.djibouti-info.com/rss", "MENA"),
            
            # MENA - Somalia
            ("Somali National News Agency", "https://www.sonna.so/rss", "MENA"),
            ("Hiiraan Online Somalia", "https://www.hiiraan.com/rss", "MENA"),
            ("Garowe Online Somalia", "https://www.garoweonline.com/rss", "MENA"),
            ("Somaliland Sun", "https://www.somalilandsun.com/rss", "MENA"),
            ("Somalia News", "https://www.somalia-news.com/rss", "MENA"),
            
            # MENA - Somaliland
            ("Somaliland News", "https://www.somaliland-news.com/rss", "MENA"),
            ("Somaliland Times", "https://www.somalilandtimes.com/rss", "MENA"),
            ("Somaliland Info", "https://www.somaliland-info.com/rss", "MENA"),
            
            # MENA - Middle East Monitor
            ("Middle East Monitor", "https://www.middleeastmonitor.com/feed/", "MENA"),
            ("Middle East Eye", "https://www.middleeasteye.net/rss", "MENA"),
            ("The New Arab", "https://www.newarab.com/rss", "MENA"),
            ("Al-Monitor", "https://www.al-monitor.com/rss", "MENA"),
            ("The Media Line", "https://themedialine.org/rss", "MENA"),
            
            # MENA - Anadolu Agency
            ("Anadolu Agency", "https://www.aa.com.tr/rss", "MENA"),
            ("Anadolu Agency Business", "https://www.aa.com.tr/business/rss", "MENA"),
            ("Anadolu Agency Economy", "https://www.aa.com.tr/economy/rss", "MENA"),
            
            # MENA - TRT World
            ("TRT World", "https://www.trtworld.com/rss", "MENA"),
            ("TRT World Business", "https://www.trtworld.com/business/rss", "MENA"),
            ("TRT World Economy", "https://www.trtworld.com/economy/rss", "MENA"),
            
            # Energy/Commodities Specialized
            ("Oil & Gas Journal", "https://www.ogj.com/rss", "Global"),
            ("Oil & Gas Journal Business", "https://www.ogj.com/business/rss", "Global"),
            ("Oil & Gas Journal Technology", "https://www.ogj.com/technology/rss", "Global"),
            ("Oil & Gas Journal Markets", "https://www.ogj.com/markets/rss", "Global"),
            ("Oil & Gas Journal Operations", "https://www.ogj.com/operations/rss", "Global"),
            ("Oil & Gas Journal Exploration", "https://www.ogj.com/exploration/rss", "Global"),
            ("Oil & Gas Journal Production", "https://www.ogj.com/production/rss", "Global"),
            ("Oil & Gas Journal Refining", "https://www.ogj.com/refining/rss", "Global"),
            ("Oil & Gas Journal Petrochemicals", "https://www.ogj.com/petrochemicals/rss", "Global"),
            ("Oil & Gas Journal Environment", "https://www.ogj.com/environment/rss", "Global"),
            ("Oil & Gas Journal Safety", "https://www.ogj.com/safety/rss", "Global"),
            ("Oil & Gas Journal Regulations", "https://www.ogj.com/regulations/rss", "Global"),
            ("Oil & Gas Journal Finance", "https://www.ogj.com/finance/rss", "Global"),
            ("Oil & Gas Journal Legal", "https://www.ogj.com/legal/rss", "Global"),
            ("Oil & Gas Journal International", "https://www.ogj.com/international/rss", "Global"),
            ("Oil & Gas Journal North America", "https://www.ogj.com/north-america/rss", "Global"),
            ("Oil & Gas Journal Europe", "https://www.ogj.com/europe/rss", "Global"),
            ("Oil & Gas Journal Asia", "https://www.ogj.com/asia/rss", "Global"),
            ("Oil & Gas Journal Middle East", "https://www.ogj.com/middle-east/rss", "Global"),
            ("Oil & Gas Journal Africa", "https://www.ogj.com/africa/rss", "Global"),
            ("Oil & Gas Journal Latin America", "https://www.ogj.com/latin-america/rss", "Global"),
            ("Oil & Gas Journal Russia", "https://www.ogj.com/russia/rss", "Global"),
            ("Oil & Gas Journal China", "https://www.ogj.com/china/rss", "Global"),
            ("Oil & Gas Journal India", "https://www.ogj.com/india/rss", "Global"),
            ("Oil & Gas Journal Brazil", "https://www.ogj.com/brazil/rss", "Global"),
            ("Oil & Gas Journal Canada", "https://www.ogj.com/canada/rss", "Global"),
            ("Oil & Gas Journal Mexico", "https://www.ogj.com/mexico/rss", "Global"),
            ("Oil & Gas Journal Norway", "https://www.ogj.com/norway/rss", "Global"),
            ("Oil & Gas Journal UK", "https://www.ogj.com/uk/rss", "Global"),
            ("Oil & Gas Journal Germany", "https://www.ogj.com/germany/rss", "Global"),
            ("Oil & Gas Journal France", "https://www.ogj.com/france/rss", "Global"),
            ("Oil & Gas Journal Italy", "https://www.ogj.com/italy/rss", "Global"),
            ("Oil & Gas Journal Spain", "https://www.ogj.com/spain/rss", "Global"),
            ("Oil & Gas Journal Netherlands", "https://www.ogj.com/netherlands/rss", "Global"),
            ("Oil & Gas Journal Belgium", "https://www.ogj.com/belgium/rss", "Global"),
            ("Oil & Gas Journal Switzerland", "https://www.ogj.com/switzerland/rss", "Global"),
            ("Oil & Gas Journal Austria", "https://www.ogj.com/austria/rss", "Global"),
            ("Oil & Gas Journal Sweden", "https://www.ogj.com/sweden/rss", "Global"),
            ("Oil & Gas Journal Denmark", "https://www.ogj.com/denmark/rss", "Global"),
            ("Oil & Gas Journal Finland", "https://www.ogj.com/finland/rss", "Global"),
            ("Oil & Gas Journal Poland", "https://www.ogj.com/poland/rss", "Global"),
            ("Oil & Gas Journal Czech Republic", "https://www.ogj.com/czech-republic/rss", "Global"),
            ("Oil & Gas Journal Hungary", "https://www.ogj.com/hungary/rss", "Global"),
            ("Oil & Gas Journal Romania", "https://www.ogj.com/romania/rss", "Global"),
            ("Oil & Gas Journal Bulgaria", "https://www.ogj.com/bulgaria/rss", "Global"),
            ("Oil & Gas Journal Croatia", "https://www.ogj.com/croatia/rss", "Global"),
            ("Oil & Gas Journal Slovenia", "https://www.ogj.com/slovenia/rss", "Global"),
            ("Oil & Gas Journal Slovakia", "https://www.ogj.com/slovakia/rss", "Global"),
            ("Oil & Gas Journal Estonia", "https://www.ogj.com/estonia/rss", "Global"),
            ("Oil & Gas Journal Latvia", "https://www.ogj.com/latvia/rss", "Global"),
            ("Oil & Gas Journal Lithuania", "https://www.ogj.com/lithuania/rss", "Global"),
            ("Oil & Gas Journal Greece", "https://www.ogj.com/greece/rss", "Global"),
            ("Oil & Gas Journal Cyprus", "https://www.ogj.com/cyprus/rss", "Global"),
            ("Oil & Gas Journal Malta", "https://www.ogj.com/malta/rss", "Global"),
            ("Oil & Gas Journal Luxembourg", "https://www.ogj.com/luxembourg/rss", "Global"),
            ("Oil & Gas Journal Ireland", "https://www.ogj.com/ireland/rss", "Global"),
            ("Oil & Gas Journal Portugal", "https://www.ogj.com/portugal/rss", "Global"),
            ("Oil & Gas Journal Iceland", "https://www.ogj.com/iceland/rss", "Global"),
            ("Oil & Gas Journal Liechtenstein", "https://www.ogj.com/liechtenstein/rss", "Global"),
            ("Oil & Gas Journal Monaco", "https://www.ogj.com/monaco/rss", "Global"),
            ("Oil & Gas Journal San Marino", "https://www.ogj.com/san-marino/rss", "Global"),
            ("Oil & Gas Journal Vatican", "https://www.ogj.com/vatican/rss", "Global"),
            ("Oil & Gas Journal Andorra", "https://www.ogj.com/andorra/rss", "Global"),
            ("Oil & Gas Journal Gibraltar", "https://www.ogj.com/gibraltar/rss", "Global"),
            ("Oil & Gas Journal Faroe Islands", "https://www.ogj.com/faroe-islands/rss", "Global"),
            ("Oil & Gas Journal Greenland", "https://www.ogj.com/greenland/rss", "Global"),
            ("Oil & Gas Journal Svalbard", "https://www.ogj.com/svalbard/rss", "Global"),
            ("Oil & Gas Journal Jan Mayen", "https://www.ogj.com/jan-mayen/rss", "Global"),
            ("Oil & Gas Journal Bouvet Island", "https://www.ogj.com/bouvet-island/rss", "Global"),
            ("Oil & Gas Journal Peter I Island", "https://www.ogj.com/peter-i-island/rss", "Global"),
            ("Oil & Gas Journal Queen Maud Land", "https://www.ogj.com/queen-maud-land/rss", "Global"),
            ("Oil & Gas Journal Ross Dependency", "https://www.ogj.com/ross-dependency/rss", "Global"),
            ("Oil & Gas Journal Australian Antarctic Territory", "https://www.ogj.com/australian-antarctic-territory/rss", "Global"),
            ("Oil & Gas Journal Adélie Land", "https://www.ogj.com/adelie-land/rss", "Global"),
            ("Oil & Gas Journal Chilean Antarctic Territory", "https://www.ogj.com/chilean-antarctic-territory/rss", "Global"),
            ("Oil & Gas Journal Argentine Antarctica", "https://www.ogj.com/argentine-antarctica/rss", "Global"),
            ("Oil & Gas Journal British Antarctic Territory", "https://www.ogj.com/british-antarctic-territory/rss", "Global"),
            ("Oil & Gas Journal French Southern and Antarctic Lands", "https://www.ogj.com/french-southern-and-antarctic-lands/rss", "Global"),
            ("Oil & Gas Journal Heard Island and McDonald Islands", "https://www.ogj.com/heard-island-and-mcdonald-islands/rss", "Global"),
            ("Oil & Gas Journal South Georgia and the South Sandwich Islands", "https://www.ogj.com/south-georgia-and-the-south-sandwich-islands/rss", "Global"),
            ("Oil & Gas Journal French Polynesia", "https://www.ogj.com/french-polynesia/rss", "Global"),
            ("Oil & Gas Journal New Caledonia", "https://www.ogj.com/new-caledonia/rss", "Global"),
            ("Oil & Gas Journal Wallis and Futuna", "https://www.ogj.com/wallis-and-futuna/rss", "Global"),
            ("Oil & Gas Journal Clipperton Island", "https://www.ogj.com/clipperton-island/rss", "Global"),
            ("Oil & Gas Journal Saint Pierre and Miquelon", "https://www.ogj.com/saint-pierre-and-miquelon/rss", "Global"),
            ("Oil & Gas Journal Saint Barthélemy", "https://www.ogj.com/saint-barthelemy/rss", "Global"),
            ("Oil & Gas Journal Saint Martin", "https://www.ogj.com/saint-martin/rss", "Global"),
            ("Oil & Gas Journal Guadeloupe", "https://www.ogj.com/guadeloupe/rss", "Global"),
            ("Oil & Gas Journal Martinique", "https://www.ogj.com/martinique/rss", "Global"),
            ("Oil & Gas Journal French Guiana", "https://www.ogj.com/french-guiana/rss", "Global"),
            ("Oil & Gas Journal Réunion", "https://www.ogj.com/reunion/rss", "Global"),
            ("Oil & Gas Journal Mayotte", "https://www.ogj.com/mayotte/rss", "Global"),
            ("Oil & Gas Journal Saint Helena", "https://www.ogj.com/saint-helena/rss", "Global"),
            ("Oil & Gas Journal Ascension Island", "https://www.ogj.com/ascension-island/rss", "Global"),
            ("Oil & Gas Journal Tristan da Cunha", "https://www.ogj.com/tristan-da-cunha/rss", "Global"),
            ("Oil & Gas Journal Falkland Islands", "https://www.ogj.com/falkland-islands/rss", "Global"),
            ("Oil & Gas Journal Pitcairn Islands", "https://www.ogj.com/pitcairn-islands/rss", "Global"),
            ("Oil & Gas Journal Norfolk Island", "https://www.ogj.com/norfolk-island/rss", "Global"),
            ("Oil & Gas Journal Christmas Island", "https://www.ogj.com/christmas-island/rss", "Global"),
            ("Oil & Gas Journal Cocos Islands", "https://www.ogj.com/cocos-islands/rss", "Global"),
            ("Oil & Gas Journal Ashmore and Cartier Islands", "https://www.ogj.com/ashmore-and-cartier-islands/rss", "Global"),
            ("Oil & Gas Journal Coral Sea Islands", "https://www.ogj.com/coral-sea-islands/rss", "Global"),
            ("Platts", "https://www.spglobal.com/platts/en/rss", "Global"),
            ("Argus Media", "https://www.argusmedia.com/rss", "Global"),
            ("Energy Voice", "https://www.energyvoice.com/rss/", "Global"),
            ("World Oil", "https://www.worldoil.com/rss/", "Global"),
            ("Rigzone", "https://www.rigzone.com/rss/", "Global"),
        ]
        
        logger.info(f"Testing {len(feeds_to_test)} RSS feeds...")
        
        for name, url, region in feeds_to_test:
            result = self.test_rss_feed(name, url, region)
            self.results.append(result)
            
            # Add delay to be respectful
            time.sleep(1)
            
        return self.results
        
    def generate_report(self):
        """Generate comprehensive test report"""
        passed = [r for r in self.results if r['status'] == 'PASSED']
        failed = [r for r in self.results if r['status'] == 'FAILED']
        
        report = {
            'summary': {
                'total_tested': len(self.results),
                'passed': len(passed),
                'failed': len(failed),
                'success_rate': len(passed) / len(self.results) * 100 if self.results else 0
            },
            'passed_sources': passed,
            'failed_sources': failed,
            'recommendations': self.get_recommendations()
        }
        
        return report
        
    def get_recommendations(self):
        """Get recommendations for production deployment"""
        passed = [r for r in self.results if r['status'] == 'PASSED']
        
        recommendations = {
            'deploy_immediately': [],
            'deploy_with_monitoring': [],
            'do_not_deploy': []
        }
        
        for result in passed:
            if result['tests_passed'] == 6 and result['response_time'] < 3:
                recommendations['deploy_immediately'].append(result['name'])
            elif result['tests_passed'] >= 5 and result['response_time'] < 5:
                recommendations['deploy_with_monitoring'].append(result['name'])
            else:
                recommendations['do_not_deploy'].append(result['name'])
                
        return recommendations

def main():
    """Main testing function"""
    tester = RSSTester()
    
    print("🔍 Starting RSS Feed Testing...")
    print("=" * 50)
    
    results = tester.test_all_feeds()
    report = tester.generate_report()
    
    # Save detailed results
    with open('rss_test_results.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print(f"\n📊 TEST RESULTS SUMMARY")
    print(f"Total Tested: {report['summary']['total_tested']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    
    print(f"\n✅ SOURCES READY FOR PRODUCTION:")
    for source in report['recommendations']['deploy_immediately']:
        print(f"  - {source}")
        
    print(f"\n⚠️  SOURCES NEED MONITORING:")
    for source in report['recommendations']['deploy_with_monitoring']:
        print(f"  - {source}")
        
    print(f"\n❌ SOURCES NOT RECOMMENDED:")
    for source in report['recommendations']['do_not_deploy']:
        print(f"  - {source}")
    
    print(f"\n📄 Detailed results saved to: rss_test_results.json")
    
    return report

if __name__ == "__main__":
    main()