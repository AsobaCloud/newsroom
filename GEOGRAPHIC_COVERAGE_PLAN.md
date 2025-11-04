# Geographic Coverage Enhancement Plan

## Overview
This document outlines the comprehensive plan to improve geographic coverage in the news scraper, focusing on Africa, Latin America, and MENA regions for energy/commodities news.

## Current State Analysis

### Existing Sources (Heavily Western/Anglo Biased)
- **North America**: BBC, CNN, Guardian, TechCrunch, Ars Technica, Wired
- **Europe**: BBC, Guardian, Al Jazeera (limited)
- **Asia**: Limited coverage through general sources
- **Africa**: Minimal coverage
- **Latin America**: Minimal coverage
- **MENA**: Limited to Al Jazeera

### Geographic Coverage Gaps
- **Africa**: ~5% of current sources
- **Latin America**: ~10% of current sources  
- **MENA**: ~15% of current sources
- **Energy/Commodities Focus**: Limited specialized sources

## Proposed New Sources

### Africa - RSS Feeds
| Source | URL | Language | Focus | Status | Notes |
|--------|-----|----------|-------|--------|-------|
| AllAfrica | `https://allafrica.com/rss/energy.rss` | English | Energy | To Test | Major African news aggregator |
| AllAfrica Business | `https://allafrica.com/rss/business.rss` | English | Business/Energy | To Test | Business focus |
| AllAfrica Politics | `https://allafrica.com/rss/politics.rss` | English | Politics | To Test | Political news |
| AllAfrica Economy | `https://allafrica.com/rss/economy.rss` | English | Economy | To Test | Economic news |
| African Business | `https://africanbusinesscentral.com/feed/` | English | Business | To Test | Pan-African business news |
| Energy Central Africa | `https://www.energycentral.com/africa/rss.xml` | English | Energy | To Test | Energy-specific |
| Business Daily Africa | `https://www.businessdailyafrica.com/rss.xml` | English | Business | To Test | Kenya-based |
| Premium Times Nigeria | `https://www.premiumtimesng.com/rss` | English | General | To Test | Nigeria-focused |
| Daily Maverick | `https://www.dailymaverick.co.za/rss/` | English | General | To Test | South Africa |
| The East African | `https://www.theeastafrican.co.ke/rss` | English | General | To Test | East Africa region |
| Vanguard Nigeria | `https://www.vanguardngr.com/rss` | English | General | To Test | Nigeria major newspaper |
| Punch Nigeria | `https://punchng.com/rss` | English | General | To Test | Nigeria major newspaper |
| This Day Nigeria | `https://www.thisdaylive.com/rss` | English | General | To Test | Nigeria business newspaper |
| The Guardian Nigeria | `https://guardian.ng/rss` | English | General | To Test | Nigeria newspaper |
| Business Day Nigeria | `https://businessday.ng/rss` | English | Business | To Test | Nigeria business newspaper |
| The Nation Nigeria | `https://thenationonlineng.net/rss` | English | General | To Test | Nigeria newspaper |
| News24 South Africa | `https://www.news24.com/rss` | English | General | To Test | South Africa major news |
| Mail & Guardian | `https://mg.co.za/rss` | English | General | To Test | South Africa newspaper |
| City Press | `https://www.news24.com/citypress/rss` | English | General | To Test | South Africa newspaper |
| Sowetan | `https://www.sowetanlive.co.za/rss` | English | General | To Test | South Africa newspaper |
| The Star | `https://www.iol.co.za/the-star/rss` | English | General | To Test | South Africa newspaper |
| Cape Times | `https://www.iol.co.za/cape-times/rss` | English | General | To Test | South Africa newspaper |
| The Citizen | `https://www.citizen.co.za/rss` | English | General | To Test | South Africa newspaper |
| Sunday Times | `https://www.timeslive.co.za/sunday-times/rss` | English | General | To Test | South Africa newspaper |
| The Times | `https://www.timeslive.co.za/the-times/rss` | English | General | To Test | South Africa newspaper |
| Business Report | `https://www.iol.co.za/business-report/rss` | English | Business | To Test | South Africa business |
| Fin24 | `https://www.fin24.com/rss` | English | Business | To Test | South Africa financial news |
| Moneyweb | `https://www.moneyweb.co.za/rss` | English | Business | To Test | South Africa financial news |
| The Standard Kenya | `https://www.standardmedia.co.ke/rss` | English | General | To Test | Kenya major newspaper |
| Nation Kenya | `https://www.nation.co.ke/rss` | English | General | To Test | Kenya major newspaper |
| Business Daily Kenya | `https://www.businessdailyafrica.com/rss` | English | Business | To Test | Kenya business newspaper |
| The Star Kenya | `https://www.the-star.co.ke/rss` | English | General | To Test | Kenya newspaper |
| Daily Nation Kenya | `https://www.nation.co.ke/rss` | English | General | To Test | Kenya newspaper |
| Capital FM Kenya | `https://www.capitalfm.co.ke/rss` | English | General | To Test | Kenya radio/news |
| KBC Kenya | `https://www.kbc.co.ke/rss` | English | General | To Test | Kenya state broadcaster |
| Al Ahram Egypt | `https://english.ahram.org.eg/rss` | English | General | To Test | Egypt major newspaper |
| Egypt Today | `https://www.egypttoday.com/rss` | English | General | To Test | Egypt newspaper |
| Daily News Egypt | `https://dailynewsegypt.com/rss` | English | General | To Test | Egypt newspaper |
| Egypt Independent | `https://www.egyptindependent.com/rss` | English | General | To Test | Egypt newspaper |
| Al Masry Al Youm | `https://www.almasryalyoum.com/rss` | English | General | To Test | Egypt newspaper |
| Morocco World News | `https://www.moroccoworldnews.com/rss` | English | General | To Test | Morocco newspaper |
| Hespress Morocco | `https://www.hespress.com/rss` | English | General | To Test | Morocco newspaper |
| Le Matin Morocco | `https://lematin.ma/rss` | French | General | To Test | Morocco newspaper |
| L'Economiste Morocco | `https://www.leconomiste.com/rss` | French | Business | To Test | Morocco business newspaper |
| Ghana Web | `https://www.ghanaweb.com/rss` | English | General | To Test | Ghana major news |
| Graphic Ghana | `https://www.graphic.com.gh/rss` | English | General | To Test | Ghana newspaper |
| Daily Graphic | `https://www.graphic.com.gh/rss` | English | General | To Test | Ghana newspaper |
| Modern Ghana | `https://www.modernghana.com/rss` | English | General | To Test | Ghana news |
| Citi FM Ghana | `https://citifmonline.com/rss` | English | General | To Test | Ghana radio/news |
| Joy News Ghana | `https://www.myjoyonline.com/rss` | English | General | To Test | Ghana news |
| Addis Fortune Ethiopia | `https://addisfortune.net/rss` | English | Business | To Test | Ethiopia business newspaper |
| The Reporter Ethiopia | `https://www.thereporterethiopia.com/rss` | English | General | To Test | Ethiopia newspaper |
| Capital Ethiopia | `https://www.capitalethiopia.com/rss` | English | General | To Test | Ethiopia newspaper |
| Walta Information Center | `https://www.waltainfo.com/rss` | English | General | To Test | Ethiopia news |
| Fana Broadcasting | `https://www.fanabc.com/rss` | English | General | To Test | Ethiopia state broadcaster |
| The Citizen Tanzania | `https://www.thecitizen.co.tz/rss` | English | General | To Test | Tanzania newspaper |
| Daily News Tanzania | `https://dailynews.co.tz/rss` | English | General | To Test | Tanzania newspaper |
| The Guardian Tanzania | `https://www.ippmedia.com/rss` | English | General | To Test | Tanzania newspaper |
| Mwananchi Tanzania | `https://www.mwananchi.co.tz/rss` | English | General | To Test | Tanzania newspaper |
| New Vision Uganda | `https://www.newvision.co.ug/rss` | English | General | To Test | Uganda newspaper |
| Daily Monitor Uganda | `https://www.monitor.co.ug/rss` | English | General | To Test | Uganda newspaper |
| The Observer Uganda | `https://observer.ug/rss` | English | General | To Test | Uganda newspaper |
| Independent Uganda | `https://www.independent.co.ug/rss` | English | General | To Test | Uganda newspaper |
| The Herald Zimbabwe | `https://www.herald.co.zw/rss` | English | General | To Test | Zimbabwe newspaper |
| NewsDay Zimbabwe | `https://www.newsday.co.zw/rss` | English | General | To Test | Zimbabwe newspaper |
| The Standard Zimbabwe | `https://www.thestandard.co.zw/rss` | English | General | To Test | Zimbabwe newspaper |
| Chronicle Zimbabwe | `https://www.chronicle.co.zw/rss` | English | General | To Test | Zimbabwe newspaper |
| The Post Zambia | `https://www.postzambia.com/rss` | English | General | To Test | Zambia newspaper |
| Times of Zambia | `https://www.times.co.zm/rss` | English | General | To Test | Zambia newspaper |
| Zambia Daily Mail | `https://www.daily-mail.co.zm/rss` | English | General | To Test | Zambia newspaper |
| Mmegi Botswana | `https://www.mmegi.bw/rss` | English | General | To Test | Botswana newspaper |
| Botswana Guardian | `https://www.botswanaguardian.co.bw/rss` | English | General | To Test | Botswana newspaper |
| The Namibian | `https://www.namibian.com.na/rss` | English | General | To Test | Namibia newspaper |
| New Era Namibia | `https://www.newera.com.na/rss` | English | General | To Test | Namibia newspaper |
| Le Soleil Senegal | `https://lesoleil.sn/rss` | French | General | To Test | Senegal newspaper |
| Sud Quotidien Senegal | `https://www.sudonline.sn/rss` | French | General | To Test | Senegal newspaper |
| Fratmat Côte d'Ivoire | `https://www.fratmat.info/rss` | French | General | To Test | Ivory Coast newspaper |
| Le Patriote Côte d'Ivoire | `https://www.lepatriote.net/rss` | French | General | To Test | Ivory Coast newspaper |
| L'Essor Mali | `https://www.essor.ml/rss` | French | General | To Test | Mali newspaper |
| Le Pays Burkina Faso | `https://lepays.bf/rss` | French | General | To Test | Burkina Faso newspaper |
| Le Sahel Niger | `https://www.lesahel.org/rss` | French | General | To Test | Niger newspaper |
| Le Progrès Chad | `https://www.leprogres.net/rss` | French | General | To Test | Chad newspaper |
| Cameroon Tribune | `https://www.cameroon-tribune.cm/rss` | French | General | To Test | Cameroon newspaper |
| The Post Cameroon | `https://www.postnewsline.com/rss` | English | General | To Test | Cameroon newspaper |
| Le Messager Cameroon | `https://www.lemessager.net/rss` | French | General | To Test | Cameroon newspaper |
| La Nouvelle République Central African Republic | `https://www.lanouvellecentrafrique.info/rss` | French | General | To Test | CAR newspaper |
| Le Potentiel DRC | `https://www.lepotentiel.cd/rss` | French | General | To Test | DRC newspaper |
| La Libre Afrique DRC | `https://www.lalibreafrique.cd/rss` | French | General | To Test | DRC newspaper |
| Le Phare DRC | `https://www.lephare.net/rss` | French | General | To Test | DRC newspaper |
| La Semaine Africaine Congo | `https://www.lasemaineafricaine.net/rss` | French | General | To Test | Congo newspaper |
| Gabon Review | `https://www.gabonreview.com/rss` | French | General | To Test | Gabon newspaper |
| L'Union Gabon | `https://www.union.sn/rss` | French | General | To Test | Gabon newspaper |
| Guinée Conakry Info | `https://www.guineeconakry.info/rss` | French | General | To Test | Guinea newspaper |
| Guinée Matin | `https://www.guineematin.com/rss` | French | General | To Test | Guinea newspaper |
| Guinée Bissau | `https://www.guineebissau.net/rss` | Portuguese | General | To Test | Guinea-Bissau newspaper |
| The Point Gambia | `https://thepoint.gm/rss` | English | General | To Test | Gambia newspaper |
| A Semana Cape Verde | `https://www.asemana.publ.cv/rss` | Portuguese | General | To Test | Cape Verde newspaper |
| Expresso das Ilhas Cape Verde | `https://expressodasilhas.cv/rss` | Portuguese | General | To Test | Cape Verde newspaper |
| STP Digital São Tomé | `https://www.stpdigital.net/rss` | Portuguese | General | To Test | São Tomé newspaper |
| Jornal de Angola | `https://jornaldeangola.sapo.ao/rss` | Portuguese | General | To Test | Angola newspaper |
| O País Angola | `https://opais.co.ao/rss` | Portuguese | General | To Test | Angola newspaper |
| Notícias Angola | `https://www.noticiasdeangola.com/rss` | Portuguese | General | To Test | Angola newspaper |
| O País Mozambique | `https://opais.co.mz/rss` | Portuguese | General | To Test | Mozambique newspaper |
| Notícias Mozambique | `https://www.noticias.co.mz/rss` | Portuguese | General | To Test | Mozambique newspaper |
| A Verdade Mozambique | `https://www.averdade.org.mz/rss` | Portuguese | General | To Test | Mozambique newspaper |
| L'Express Madagascar | `https://www.lexpress.mg/rss` | French | General | To Test | Madagascar newspaper |
| Madagascar Tribune | `https://www.madagascar-tribune.com/rss` | French | General | To Test | Madagascar newspaper |
| Midi Madagasikara | `https://www.midi-madagasikara.mg/rss` | French | General | To Test | Madagascar newspaper |
| L'Express Maurice | `https://www.lexpress.mu/rss` | French | General | To Test | Mauritius newspaper |
| Le Mauricien | `https://www.lemauricien.com/rss` | French | General | To Test | Mauritius newspaper |
| Seychelles Nation | `https://www.nation.sc/rss` | English | General | To Test | Seychelles newspaper |
| Al-Watwan Comoros | `https://www.alwatwan.net/rss` | French | General | To Test | Comoros newspaper |
| La Nation Djibouti | `https://www.lanation.dj/rss` | French | General | To Test | Djibouti newspaper |
| Somali National News Agency | `https://www.sonna.so/rss` | English | General | To Test | Somalia news agency |
| Hiiraan Online Somalia | `https://www.hiiraan.com/rss` | English | General | To Test | Somalia news |
| Garowe Online Somalia | `https://www.garoweonline.com/rss` | English | General | To Test | Somalia news |
| Eritrea Profile | `https://www.eritrea-profile.net/rss` | English | General | To Test | Eritrea newspaper |
| Sudan Tribune | `https://www.sudantribune.com/rss` | English | General | To Test | Sudan newspaper |
| Radio Dabanga Sudan | `https://www.dabangasudan.org/rss` | English | General | To Test | Sudan radio/news |
| South Sudan News Agency | `https://www.southsudannewsagency.com/rss` | English | General | To Test | South Sudan news |
| Eye Radio South Sudan | `https://eyeradio.org/rss` | English | General | To Test | South Sudan radio/news |
| Libya Herald | `https://www.libyaherald.com/rss` | English | General | To Test | Libya newspaper |
| Libya Observer | `https://www.libyaobserver.ly/rss` | English | General | To Test | Libya newspaper |
| Tunis Afrique Presse | `https://www.tap.info.tn/rss` | French | General | To Test | Tunisia news agency |
| La Presse Tunisia | `https://www.lapresse.tn/rss` | French | General | To Test | Tunisia newspaper |
| Le Temps Tunisia | `https://www.letemps.com.tn/rss` | French | General | To Test | Tunisia newspaper |
| El Watan Algeria | `https://www.elwatan.com/rss` | French | General | To Test | Algeria newspaper |
| Liberté Algeria | `https://www.liberte-algerie.com/rss` | French | General | To Test | Algeria newspaper |
| El Moudjahid Algeria | `https://www.elmoudjahid.com/rss` | French | General | To Test | Algeria newspaper |
| Le Quotidien d'Oran Algeria | `https://www.lequotidien-oran.com/rss` | French | General | To Test | Algeria newspaper |
| La Tribune Algérienne | `https://www.latribune-online.com/rss` | French | General | To Test | Algeria newspaper |
| Le Matin d'Algérie | `https://www.lematindz.net/rss` | French | General | To Test | Algeria newspaper |
| L'Expression Algeria | `https://www.lexpressiondz.com/rss` | French | General | To Test | Algeria newspaper |
| Le Soir d'Algérie | `https://www.lesoirdalgerie.com/rss` | French | General | To Test | Algeria newspaper |
| Le Jeune Indépendant Algeria | `https://www.lejeune-independant.com/rss` | French | General | To Test | Algeria newspaper |
| Le Courrier d'Algérie | `https://www.lecourrier-dalgerie.com/rss` | French | General | To Test | Algeria newspaper |
| Le Temps d'Algérie | `https://www.letemps-dz.com/rss` | French | General | To Test | Algeria newspaper |
| Le Buteur Algeria | `https://www.lebuteur.com/rss` | French | General | To Test | Algeria newspaper |
| Le Financier Algeria | `https://www.lefinancier-dz.com/rss` | French | General | To Test | Algeria newspaper |
| Le Maghreb Algeria | `https://www.lemaghreb-dz.com/rss` | French | General | To Test | Algeria newspaper |
| Le Quotidien d'Algérie | `https://www.lequotidien-algerie.org/rss` | French | General | To Test | Algeria newspaper |

### Africa - Direct Scraping
| Source | URL | Language | Focus | Status | Notes |
|--------|-----|----------|-------|--------|-------|
| AllAfrica Energy | `https://allafrica.com/energy/` | English | Energy | To Test | Direct energy section |
| African Business Central | `https://africanbusinesscentral.com/` | English | Business | To Test | Business news |
| Energy Central Africa | `https://www.energycentral.com/africa/` | English | Energy | To Test | Energy news |

### Latin America - RSS Feeds
| Source | URL | Language | Focus | Status | Notes |
|--------|-----|----------|-------|--------|-------|
| Folha de S.Paulo Energia | `https://feeds.folha.uol.com.br/folha/energia/rss091.xml` | Portuguese | Energy | To Test | Brazil's major newspaper |
| Folha de S.Paulo Economia | `https://feeds.folha.uol.com.br/folha/economia/rss091.xml` | Portuguese | Economy | To Test | Brazil economy section |
| Folha de S.Paulo Mercado | `https://feeds.folha.uol.com.br/folha/mercado/rss091.xml` | Portuguese | Business | To Test | Brazil market news |
| O Globo Brasil | `https://oglobo.globo.com/rss.xml` | Portuguese | General | To Test | Brazil major newspaper |
| O Estado de S.Paulo | `https://www.estadao.com.br/rss` | Portuguese | General | To Test | Brazil major newspaper |
| Jornal do Brasil | `https://www.jb.com.br/rss` | Portuguese | General | To Test | Brazil major newspaper |
| Correio Braziliense | `https://www.correiobraziliense.com.br/rss` | Portuguese | General | To Test | Brazil newspaper |
| Zero Hora | `https://gauchazh.clicrbs.com.br/rss` | Portuguese | General | To Test | Brazil regional newspaper |
| Gazeta do Povo | `https://www.gazetadopovo.com.br/rss` | Portuguese | General | To Test | Brazil regional newspaper |
| Valor Econômico | `https://www.valor.com.br/rss` | Portuguese | Business/Energy | To Test | Brazil business newspaper |
| Exame Brasil | `https://exame.com/rss` | Portuguese | Business | To Test | Brazil business magazine |
| IstoÉ Dinheiro | `https://www.istoedinheiro.com.br/rss` | Portuguese | Business | To Test | Brazil business magazine |
| Época Negócios | `https://epocanegocios.globo.com/rss` | Portuguese | Business | To Test | Brazil business magazine |
| InfoMoney | `https://www.infomoney.com.br/rss` | Portuguese | Business | To Test | Brazil financial news |
| Money Report | `https://www.moneyreport.com.br/rss` | Portuguese | Business | To Test | Brazil financial news |
| Investimentos e Notícias | `https://www.investimentosenoticias.com.br/rss` | Portuguese | Business | To Test | Brazil investment news |
| La Nación Argentina | `https://www.lanacion.com.ar/rss/energia` | Spanish | Energy | To Test | Argentina major newspaper |
| La Nación Argentina Economía | `https://www.lanacion.com.ar/rss/economia` | Spanish | Economy | To Test | Argentina economy section |
| Clarín Argentina | `https://www.clarin.com/rss` | Spanish | General | To Test | Argentina major newspaper |
| Página/12 Argentina | `https://www.pagina12.com.ar/rss` | Spanish | General | To Test | Argentina newspaper |
| La Voz del Interior | `https://www.lavoz.com.ar/rss` | Spanish | General | To Test | Argentina regional newspaper |
| El Cronista Argentina | `https://www.cronista.com/rss` | Spanish | Business | To Test | Argentina business newspaper |
| Ámbito Financiero Argentina | `https://www.ambito.com/rss` | Spanish | Business | To Test | Argentina financial newspaper |
| El País Brasil | `https://brasil.elpais.com/rss/` | Portuguese | General | To Test | Spanish newspaper Brazil edition |
| El País Economía | `https://brasil.elpais.com/economia/rss/` | Portuguese | Economy | To Test | Brazil economy section |
| El Mercurio Chile | `https://www.elmercurio.com/rss/` | Spanish | General | To Test | Chile major newspaper |
| La Tercera Chile | `https://www.latercera.com/rss` | Spanish | General | To Test | Chile major newspaper |
| El Mostrador Chile | `https://www.elmostrador.cl/rss` | Spanish | General | To Test | Chile newspaper |
| La Segunda Chile | `https://www.lasegunda.com/rss` | Spanish | General | To Test | Chile newspaper |
| El Tiempo Colombia | `https://www.eltiempo.com/rss/` | Spanish | General | To Test | Colombia major newspaper |
| El Espectador Colombia | `https://www.elespectador.com/rss` | Spanish | General | To Test | Colombia newspaper |
| El Colombiano | `https://www.elcolombiano.com/rss` | Spanish | General | To Test | Colombia newspaper |
| Portafolio Colombia | `https://www.portafolio.co/rss` | Spanish | Business | To Test | Colombia business newspaper |
| La República Colombia | `https://www.larepublica.co/rss` | Spanish | Business | To Test | Colombia business newspaper |
| El Universal México | `https://www.eluniversal.com.mx/rss/` | Spanish | General | To Test | Mexico major newspaper |
| El Universal México Economía | `https://www.eluniversal.com.mx/economia/rss` | Spanish | Economy | To Test | Mexico economy section |
| Reforma México | `https://www.reforma.com/rss` | Spanish | General | To Test | Mexico major newspaper |
| La Jornada México | `https://www.jornada.com.mx/rss` | Spanish | General | To Test | Mexico newspaper |
| Excélsior México | `https://www.excelsior.com.mx/rss` | Spanish | General | To Test | Mexico newspaper |
| Milenio México | `https://www.milenio.com/rss` | Spanish | General | To Test | Mexico newspaper |
| El Financiero México | `https://www.elfinanciero.com.mx/rss` | Spanish | Business | To Test | Mexico business newspaper |
| El Economista México | `https://www.eleconomista.com.mx/rss` | Spanish | Business | To Test | Mexico business newspaper |
| Expansión México | `https://expansion.mx/rss` | Spanish | Business | To Test | Mexico business magazine |
| El Comercio Perú | `https://elcomercio.pe/rss/` | Spanish | General | To Test | Peru major newspaper |
| El Comercio Perú Economía | `https://elcomercio.pe/economia/rss/` | Spanish | Economy | To Test | Peru economy section |
| La República Perú | `https://larepublica.pe/rss` | Spanish | General | To Test | Peru newspaper |
| Perú 21 | `https://peru21.pe/rss` | Spanish | General | To Test | Peru newspaper |
| Gestión Perú | `https://gestion.pe/rss` | Spanish | Business | To Test | Peru business newspaper |
| El Peruano | `https://www.elperuano.pe/rss` | Spanish | General | To Test | Peru official newspaper |
| Correo Perú | `https://diariocorreo.pe/rss` | Spanish | General | To Test | Peru newspaper |
| Trome Perú | `https://trome.pe/rss` | Spanish | General | To Test | Peru newspaper |
| Ojo Perú | `https://ojo.pe/rss` | Spanish | General | To Test | Peru newspaper |
| El Nacional Venezuela | `https://www.el-nacional.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Universal Venezuela | `https://www.eluniversal.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| Últimas Noticias Venezuela | `https://www.ultimasnoticias.com.ve/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Tiempo Venezuela | `https://www.eltiempo.com.ve/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Mundo Venezuela | `https://www.elmundo.com.ve/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Impulso Venezuela | `https://www.elimpulso.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Carabobeño Venezuela | `https://www.elcarabobeño.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Diario de Caracas | `https://www.eldiario.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Nuevo País Venezuela | `https://www.elnuevopais.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Nacional Venezuela | `https://www.el-nacional.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Universal Venezuela | `https://www.eluniversal.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| Últimas Noticias Venezuela | `https://www.ultimasnoticias.com.ve/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Tiempo Venezuela | `https://www.eltiempo.com.ve/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Mundo Venezuela | `https://www.elmundo.com.ve/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Impulso Venezuela | `https://www.elimpulso.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Carabobeño Venezuela | `https://www.elcarabobeño.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Diario de Caracas | `https://www.eldiario.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Nuevo País Venezuela | `https://www.elnuevopais.com/rss` | Spanish | General | To Test | Venezuela newspaper |
| El Comercio Ecuador | `https://www.elcomercio.com/rss` | Spanish | General | To Test | Ecuador major newspaper |
| El Universo Ecuador | `https://www.eluniverso.com/rss` | Spanish | General | To Test | Ecuador newspaper |
| La Hora Ecuador | `https://www.lahora.com.ec/rss` | Spanish | General | To Test | Ecuador newspaper |
| El Telégrafo Ecuador | `https://www.eltelegrafo.com.ec/rss` | Spanish | General | To Test | Ecuador newspaper |
| El Mercurio Ecuador | `https://www.elmercurio.com.ec/rss` | Spanish | General | To Test | Ecuador newspaper |
| El Diario Ecuador | `https://www.eldiario.ec/rss` | Spanish | General | To Test | Ecuador newspaper |
| El Tiempo Ecuador | `https://www.eltiempo.com.ec/rss` | Spanish | General | To Test | Ecuador newspaper |
| El Comercio Ecuador | `https://www.elcomercio.com/rss` | Spanish | General | To Test | Ecuador major newspaper |
| El Universo Ecuador | `https://www.eluniverso.com/rss` | Spanish | General | To Test | Ecuador newspaper |
| La Hora Ecuador | `https://www.lahora.com.ec/rss` | Spanish | General | To Test | Ecuador newspaper |
| El Telégrafo Ecuador | `https://www.eltelegrafo.com.ec/rss` | Spanish | General | To Test | Ecuador newspaper |
| El Mercurio Ecuador | `https://www.elmercurio.com.ec/rss` | Spanish | General | To Test | Ecuador newspaper |
| El Diario Ecuador | `https://www.eldiario.ec/rss` | Spanish | General | To Test | Ecuador newspaper |
| El Tiempo Ecuador | `https://www.eltiempo.com.ec/rss` | Spanish | General | To Test | Ecuador newspaper |
| La Razón Bolivia | `https://www.la-razon.com/rss` | Spanish | General | To Test | Bolivia major newspaper |
| El Deber Bolivia | `https://www.eldeber.com.bo/rss` | Spanish | General | To Test | Bolivia newspaper |
| Los Tiempos Bolivia | `https://www.lostiempos.com/rss` | Spanish | General | To Test | Bolivia newspaper |
| El Diario Bolivia | `https://www.eldiario.net/rss` | Spanish | General | To Test | Bolivia newspaper |
| La Prensa Bolivia | `https://www.laprensa.com.bo/rss` | Spanish | General | To Test | Bolivia newspaper |
| El País Bolivia | `https://www.elpais.com.bo/rss` | Spanish | General | To Test | Bolivia newspaper |
| El Mundo Bolivia | `https://www.elmundo.com.bo/rss` | Spanish | General | To Test | Bolivia newspaper |
| El Sol Bolivia | `https://www.elsol.com.bo/rss` | Spanish | General | To Test | Bolivia newspaper |
| ABC Color Paraguay | `https://www.abc.com.py/rss` | Spanish | General | To Test | Paraguay major newspaper |
| Última Hora Paraguay | `https://www.ultimahora.com/rss` | Spanish | General | To Test | Paraguay newspaper |
| La Nación Paraguay | `https://www.lanacion.com.py/rss` | Spanish | General | To Test | Paraguay newspaper |
| El Diario Paraguay | `https://www.eldiario.com.py/rss` | Spanish | General | To Test | Paraguay newspaper |
| Hoy Paraguay | `https://www.hoy.com.py/rss` | Spanish | General | To Test | Paraguay newspaper |
| El País Paraguay | `https://www.elpais.com.py/rss` | Spanish | General | To Test | Paraguay newspaper |
| El Mundo Paraguay | `https://www.elmundo.com.py/rss` | Spanish | General | To Test | Paraguay newspaper |
| El Sol Paraguay | `https://www.elsol.com.py/rss` | Spanish | General | To Test | Paraguay newspaper |
| El Observador Uruguay | `https://www.elobservador.com.uy/rss` | Spanish | General | To Test | Uruguay major newspaper |
| El País Uruguay | `https://www.elpais.com.uy/rss` | Spanish | General | To Test | Uruguay newspaper |
| La República Uruguay | `https://www.larepublica.com.uy/rss` | Spanish | General | To Test | Uruguay newspaper |
| El Diario Uruguay | `https://www.eldiario.com.uy/rss` | Spanish | General | To Test | Uruguay newspaper |
| El Telégrafo Uruguay | `https://www.eltelegrafo.com.uy/rss` | Spanish | General | To Test | Uruguay newspaper |
| El Mercurio Uruguay | `https://www.elmercurio.com.uy/rss` | Spanish | General | To Test | Uruguay newspaper |
| El Tiempo Uruguay | `https://www.eltiempo.com.uy/rss` | Spanish | General | To Test | Uruguay newspaper |
| El Mundo Uruguay | `https://www.elmundo.com.uy/rss` | Spanish | General | To Test | Uruguay newspaper |
| El Sol Uruguay | `https://www.elsol.com.uy/rss` | Spanish | General | To Test | Uruguay newspaper |
| El Nacional Guyana | `https://www.elnacional.com.gy/rss` | English | General | To Test | Guyana newspaper |
| Stabroek News Guyana | `https://www.stabroeknews.com/rss` | English | General | To Test | Guyana newspaper |
| Kaieteur News Guyana | `https://www.kaieteurnewsonline.com/rss` | English | General | To Test | Guyana newspaper |
| Guyana Chronicle | `https://www.guyanachronicle.com/rss` | English | General | To Test | Guyana newspaper |
| Demerara Waves Guyana | `https://www.demerarawaves.com/rss` | English | General | To Test | Guyana news |
| News Room Guyana | `https://www.newsroom.gy/rss` | English | General | To Test | Guyana news |
| El Nacional Suriname | `https://www.elnacional.com.sr/rss` | Spanish | General | To Test | Suriname newspaper |
| De Ware Tijd Suriname | `https://www.dwtonline.com/rss` | Dutch | General | To Test | Suriname newspaper |
| Suriname Herald | `https://www.surinameherald.com/rss` | Dutch | General | To Test | Suriname newspaper |
| Dagblad Suriname | `https://www.dagbladsuriname.com/rss` | Dutch | General | To Test | Suriname newspaper |
| Suriname Times | `https://www.surinametimes.com/rss` | English | General | To Test | Suriname newspaper |
| Suriname News | `https://www.surinamenews.com/rss` | English | General | To Test | Suriname news |
| France Guyane | `https://www.franceguyane.fr/rss` | French | General | To Test | French Guiana newspaper |
| La 1ère Guyane | `https://la1ere.francetvinfo.fr/guyane/rss` | French | General | To Test | French Guiana news |
| Guyane la 1ère | `https://guyane.la1ere.fr/rss` | French | General | To Test | French Guiana news |
| Le Journal de la Guyane | `https://www.lejournaldelaguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| La Dépêche de la Guyane | `https://www.ladepecheguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Progrès Guyane | `https://www.leprogresguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Soir Guyane | `https://www.lesoirguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Matin Guyane | `https://www.lematinguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Temps Guyane | `https://www.letempsguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Buteur Guyane | `https://www.lebuteurguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Financier Guyane | `https://www.lefinancierguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Maghreb Guyane | `https://www.lemaghrebguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Quotidien Guyane | `https://www.lequotidienguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Soir Guyane | `https://www.lesoirguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Temps Guyane | `https://www.letempsguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Buteur Guyane | `https://www.lebuteurguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Financier Guyane | `https://www.lefinancierguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Maghreb Guyane | `https://www.lemaghrebguyane.com/rss` | French | General | To Test | French Guiana newspaper |
| Le Quotidien Guyane | `https://www.lequotidienguyane.com/rss` | French | General | To Test | French Guiana newspaper |

### Latin America - Direct Scraping
| Source | URL | Language | Focus | Status | Notes |
|--------|-----|----------|-------|--------|-------|
| Valor Econômico Energia | `https://www.valor.com.br/energia` | Portuguese | Energy | To Test | Brazil energy section |
| La Nación Energía | `https://www.lanacion.com.ar/energia` | Spanish | Energy | To Test | Argentina energy section |
| El País Economía | `https://brasil.elpais.com/economia/` | Portuguese | Business | To Test | Brazil economy section |

### MENA - RSS Feeds
| Source | URL | Language | Focus | Status | Notes |
|--------|-----|----------|-------|--------|-------|
| Al Arabiya English | `https://english.alarabiya.net/rss.xml` | English | General | To Test | Saudi-owned, English |
| Al Arabiya Business | `https://english.alarabiya.net/business/rss.xml` | English | Business | To Test | Saudi business news |
| Al Arabiya Economy | `https://english.alarabiya.net/economy/rss.xml` | English | Economy | To Test | Saudi economy news |
| Gulf News | `https://gulfnews.com/rss` | English | General | To Test | UAE major newspaper |
| Gulf News Business | `https://gulfnews.com/business/rss` | English | Business | To Test | UAE business news |
| Gulf News Economy | `https://gulfnews.com/economy/rss` | English | Economy | To Test | UAE economy news |
| Middle East Monitor | `https://www.middleeastmonitor.com/feed/` | English | General | To Test | Independent news |
| Arab News | `https://www.arabnews.com/rss` | English | General | To Test | Saudi newspaper |
| Arab News Business | `https://www.arabnews.com/business/rss` | English | Business | To Test | Saudi business news |
| Arab News Economy | `https://www.arabnews.com/economy/rss` | English | Economy | To Test | Saudi economy news |
| The National UAE | `https://www.thenational.ae/rss` | English | General | To Test | UAE newspaper |
| The National UAE Business | `https://www.thenational.ae/business/rss` | English | Business | To Test | UAE business news |
| The National UAE Economy | `https://www.thenational.ae/economy/rss` | English | Economy | To Test | UAE economy news |
| Daily Sabah | `https://www.dailysabah.com/rss` | English | General | To Test | Turkey newspaper |
| Daily Sabah Business | `https://www.dailysabah.com/business/rss` | English | Business | To Test | Turkey business news |
| Daily Sabah Economy | `https://www.dailysabah.com/economy/rss` | English | Economy | To Test | Turkey economy news |
| Jerusalem Post | `https://www.jpost.com/rss` | English | General | To Test | Israel newspaper |
| Jerusalem Post Business | `https://www.jpost.com/business/rss` | English | Business | To Test | Israel business news |
| Jerusalem Post Economy | `https://www.jpost.com/economy/rss` | English | Economy | To Test | Israel economy news |
| Haaretz | `https://www.haaretz.com/rss` | English | General | To Test | Israel newspaper |
| Haaretz Business | `https://www.haaretz.com/business/rss` | English | Business | To Test | Israel business news |
| Haaretz Economy | `https://www.haaretz.com/economy/rss` | English | Economy | To Test | Israel economy news |
| Al Jazeera English | `https://www.aljazeera.com/rss` | English | General | To Test | Qatar-based news |
| Al Jazeera Business | `https://www.aljazeera.com/business/rss` | English | Business | To Test | Qatar business news |
| Al Jazeera Economy | `https://www.aljazeera.com/economy/rss` | English | Economy | To Test | Qatar economy news |
| Middle East Eye | `https://www.middleeasteye.net/rss` | English | General | To Test | Independent news |
| Middle East Eye Business | `https://www.middleeasteye.net/business/rss` | English | Business | To Test | Independent business news |
| Middle East Eye Economy | `https://www.middleeasteye.net/economy/rss` | English | Economy | To Test | Independent economy news |
| The New Arab | `https://www.newarab.com/rss` | English | General | To Test | Independent news |
| The New Arab Business | `https://www.newarab.com/business/rss` | English | Business | To Test | Independent business news |
| The New Arab Economy | `https://www.newarab.com/economy/rss` | English | Economy | To Test | Independent economy news |
| Asharq Al-Awsat | `https://english.aawsat.com/rss` | English | General | To Test | Saudi newspaper |
| Asharq Al-Awsat Business | `https://english.aawsat.com/business/rss` | English | Business | To Test | Saudi business news |
| Asharq Al-Awsat Economy | `https://english.aawsat.com/economy/rss` | English | Economy | To Test | Saudi economy news |
| Al-Monitor | `https://www.al-monitor.com/rss` | English | General | To Test | Independent news |
| Al-Monitor Business | `https://www.al-monitor.com/business/rss` | English | Business | To Test | Independent business news |
| Al-Monitor Economy | `https://www.al-monitor.com/economy/rss` | English | Economy | To Test | Independent economy news |
| The Media Line | `https://themedialine.org/rss` | English | General | To Test | Independent news |
| The Media Line Business | `https://themedialine.org/business/rss` | English | Business | To Test | Independent business news |
| The Media Line Economy | `https://themedialine.org/economy/rss` | English | Economy | To Test | Independent economy news |
| Anadolu Agency | `https://www.aa.com.tr/rss` | English | General | To Test | Turkey news agency |
| Anadolu Agency Business | `https://www.aa.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Anadolu Agency Economy | `https://www.aa.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| TRT World | `https://www.trtworld.com/rss` | English | General | To Test | Turkey state broadcaster |
| TRT World Business | `https://www.trtworld.com/business/rss` | English | Business | To Test | Turkey business news |
| TRT World Economy | `https://www.trtworld.com/economy/rss` | English | Economy | To Test | Turkey economy news |
| Hurriyet Daily News | `https://www.hurriyetdailynews.com/rss` | English | General | To Test | Turkey newspaper |
| Hurriyet Daily News Business | `https://www.hurriyetdailynews.com/business/rss` | English | Business | To Test | Turkey business news |
| Hurriyet Daily News Economy | `https://www.hurriyetdailynews.com/economy/rss` | English | Economy | To Test | Turkey economy news |
| Today's Zaman | `https://www.todayszaman.com/rss` | English | General | To Test | Turkey newspaper |
| Today's Zaman Business | `https://www.todayszaman.com/business/rss` | English | Business | To Test | Turkey business news |
| Today's Zaman Economy | `https://www.todayszaman.com/economy/rss` | English | Economy | To Test | Turkey economy news |
| Zaman | `https://www.zaman.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Zaman Business | `https://www.zaman.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Zaman Economy | `https://www.zaman.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Milliyet | `https://www.milliyet.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Milliyet Business | `https://www.milliyet.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Milliyet Economy | `https://www.milliyet.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Sabah | `https://www.sabah.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Sabah Business | `https://www.sabah.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Sabah Economy | `https://www.sabah.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Şafak | `https://www.yenisafak.com/rss` | English | General | To Test | Turkey newspaper |
| Yeni Şafak Business | `https://www.yenisafak.com/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Şafak Economy | `https://www.yenisafak.com/economy/rss` | English | Economy | To Test | Turkey economy news |
| Star | `https://www.star.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Star Business | `https://www.star.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Star Economy | `https://www.star.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Akşam | `https://www.aksam.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Akşam Business | `https://www.aksam.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Akşam Economy | `https://www.aksam.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Cumhuriyet | `https://www.cumhuriyet.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Cumhuriyet Business | `https://www.cumhuriyet.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Cumhuriyet Economy | `https://www.cumhuriyet.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Sözcü | `https://www.sozcu.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Sözcü Business | `https://www.sozcu.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Sözcü Economy | `https://www.sozcu.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Hürriyet | `https://www.hurriyet.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Hürriyet Business | `https://www.hurriyet.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Hürriyet Economy | `https://www.hurriyet.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Posta | `https://www.posta.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Posta Business | `https://www.posta.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Posta Economy | `https://www.posta.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Takvim | `https://www.takvim.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Takvim Business | `https://www.takvim.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Takvim Economy | `https://www.takvim.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Vatan | `https://www.gazetevatan.com/rss` | English | General | To Test | Turkey newspaper |
| Vatan Business | `https://www.gazetevatan.com/business/rss` | English | Business | To Test | Turkey business news |
| Vatan Economy | `https://www.gazetevatan.com/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Akit | `https://www.yeniakit.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Yeni Akit Business | `https://www.yeniakit.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Akit Economy | `https://www.yeniakit.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Çağ | `https://www.yenicag.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Yeni Çağ Business | `https://www.yenicag.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Çağ Economy | `https://www.yenicag.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Mesaj | `https://www.yenimesaj.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Yeni Mesaj Business | `https://www.yenimesaj.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Mesaj Economy | `https://www.yenimesaj.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Şafak | `https://www.yenisafak.com/rss` | English | General | To Test | Turkey newspaper |
| Yeni Şafak Business | `https://www.yenisafak.com/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Şafak Economy | `https://www.yenisafak.com/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Asır | `https://www.yeniasir.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Yeni Asır Business | `https://www.yeniasir.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Asır Economy | `https://www.yeniasir.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Asya | `https://www.yeniasya.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Yeni Asya Business | `https://www.yeniasya.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Asya Economy | `https://www.yeniasya.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Birlik | `https://www.yenibirlik.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Yeni Birlik Business | `https://www.yenibirlik.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Birlik Economy | `https://www.yenibirlik.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Çağ | `https://www.yenicag.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Yeni Çağ Business | `https://www.yenicag.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Çağ Economy | `https://www.yenicag.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Mesaj | `https://www.yenimesaj.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Yeni Mesaj Business | `https://www.yenimesaj.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Mesaj Economy | `https://www.yenimesaj.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Şafak | `https://www.yenisafak.com/rss` | English | General | To Test | Turkey newspaper |
| Yeni Şafak Business | `https://www.yenisafak.com/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Şafak Economy | `https://www.yenisafak.com/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Asır | `https://www.yeniasir.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Yeni Asır Business | `https://www.yeniasir.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Asır Economy | `https://www.yeniasir.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Asya | `https://www.yeniasya.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Yeni Asya Business | `https://www.yeniasya.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Asya Economy | `https://www.yeniasya.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |
| Yeni Birlik | `https://www.yenibirlik.com.tr/rss` | English | General | To Test | Turkey newspaper |
| Yeni Birlik Business | `https://www.yenibirlik.com.tr/business/rss` | English | Business | To Test | Turkey business news |
| Yeni Birlik Economy | `https://www.yenibirlik.com.tr/economy/rss` | English | Economy | To Test | Turkey economy news |

### MENA - Direct Scraping
| Source | URL | Language | Focus | Status | Notes |
|--------|-----|----------|-------|--------|-------|
| Al Arabiya Business | `https://english.alarabiya.net/business` | English | Business | To Test | Business section |
| Gulf News Business | `https://gulfnews.com/business` | English | Business | To Test | Business section |
| Arab News Business | `https://www.arabnews.com/business` | English | Business | To Test | Business section |

### Energy/Commodities Specialized Sources
| Source | URL | Language | Focus | Status | Notes |
|--------|-----|----------|-------|--------|-------|
| Oil & Gas Journal | `https://www.ogj.com/rss` | English | Oil/Gas | To Test | Industry publication |
| Oil & Gas Journal Business | `https://www.ogj.com/business/rss` | English | Oil/Gas Business | To Test | Industry business news |
| Oil & Gas Journal Technology | `https://www.ogj.com/technology/rss` | English | Oil/Gas Technology | To Test | Industry technology news |
| Oil & Gas Journal Markets | `https://www.ogj.com/markets/rss` | English | Oil/Gas Markets | To Test | Industry market news |
| Oil & Gas Journal Operations | `https://www.ogj.com/operations/rss` | English | Oil/Gas Operations | To Test | Industry operations news |
| Oil & Gas Journal Exploration | `https://www.ogj.com/exploration/rss` | English | Oil/Gas Exploration | To Test | Industry exploration news |
| Oil & Gas Journal Production | `https://www.ogj.com/production/rss` | English | Oil/Gas Production | To Test | Industry production news |
| Oil & Gas Journal Refining | `https://www.ogj.com/refining/rss` | English | Oil/Gas Refining | To Test | Industry refining news |
| Oil & Gas Journal Petrochemicals | `https://www.ogj.com/petrochemicals/rss` | English | Oil/Gas Petrochemicals | To Test | Industry petrochemicals news |
| Oil & Gas Journal Environment | `https://www.ogj.com/environment/rss` | English | Oil/Gas Environment | To Test | Industry environment news |
| Oil & Gas Journal Safety | `https://www.ogj.com/safety/rss` | English | Oil/Gas Safety | To Test | Industry safety news |
| Oil & Gas Journal Regulations | `https://www.ogj.com/regulations/rss` | English | Oil/Gas Regulations | To Test | Industry regulations news |
| Oil & Gas Journal Finance | `https://www.ogj.com/finance/rss` | English | Oil/Gas Finance | To Test | Industry finance news |
| Oil & Gas Journal Legal | `https://www.ogj.com/legal/rss` | English | Oil/Gas Legal | To Test | Industry legal news |
| Oil & Gas Journal International | `https://www.ogj.com/international/rss` | English | Oil/Gas International | To Test | Industry international news |
| Oil & Gas Journal North America | `https://www.ogj.com/north-america/rss` | English | Oil/Gas North America | To Test | Industry North America news |
| Oil & Gas Journal Europe | `https://www.ogj.com/europe/rss` | English | Oil/Gas Europe | To Test | Industry Europe news |
| Oil & Gas Journal Asia | `https://www.ogj.com/asia/rss` | English | Oil/Gas Asia | To Test | Industry Asia news |
| Oil & Gas Journal Middle East | `https://www.ogj.com/middle-east/rss` | English | Oil/Gas Middle East | To Test | Industry Middle East news |
| Oil & Gas Journal Africa | `https://www.ogj.com/africa/rss` | English | Oil/Gas Africa | To Test | Industry Africa news |
| Oil & Gas Journal Latin America | `https://www.ogj.com/latin-america/rss` | English | Oil/Gas Latin America | To Test | Industry Latin America news |
| Oil & Gas Journal Russia | `https://www.ogj.com/russia/rss` | English | Oil/Gas Russia | To Test | Industry Russia news |
| Oil & Gas Journal China | `https://www.ogj.com/china/rss` | English | Oil/Gas China | To Test | Industry China news |
| Oil & Gas Journal India | `https://www.ogj.com/india/rss` | English | Oil/Gas India | To Test | Industry India news |
| Oil & Gas Journal Brazil | `https://www.ogj.com/brazil/rss` | English | Oil/Gas Brazil | To Test | Industry Brazil news |
| Oil & Gas Journal Canada | `https://www.ogj.com/canada/rss` | English | Oil/Gas Canada | To Test | Industry Canada news |
| Oil & Gas Journal Mexico | `https://www.ogj.com/mexico/rss` | English | Oil/Gas Mexico | To Test | Industry Mexico news |
| Oil & Gas Journal Norway | `https://www.ogj.com/norway/rss` | English | Oil/Gas Norway | To Test | Industry Norway news |
| Oil & Gas Journal UK | `https://www.ogj.com/uk/rss` | English | Oil/Gas UK | To Test | Industry UK news |
| Oil & Gas Journal Germany | `https://www.ogj.com/germany/rss` | English | Oil/Gas Germany | To Test | Industry Germany news |
| Oil & Gas Journal France | `https://www.ogj.com/france/rss` | English | Oil/Gas France | To Test | Industry France news |
| Oil & Gas Journal Italy | `https://www.ogj.com/italy/rss` | English | Oil/Gas Italy | To Test | Industry Italy news |
| Oil & Gas Journal Spain | `https://www.ogj.com/spain/rss` | English | Oil/Gas Spain | To Test | Industry Spain news |
| Oil & Gas Journal Netherlands | `https://www.ogj.com/netherlands/rss` | English | Oil/Gas Netherlands | To Test | Industry Netherlands news |
| Oil & Gas Journal Belgium | `https://www.ogj.com/belgium/rss` | English | Oil/Gas Belgium | To Test | Industry Belgium news |
| Oil & Gas Journal Switzerland | `https://www.ogj.com/switzerland/rss` | English | Oil/Gas Switzerland | To Test | Industry Switzerland news |
| Oil & Gas Journal Austria | `https://www.ogj.com/austria/rss` | English | Oil/Gas Austria | To Test | Industry Austria news |
| Oil & Gas Journal Sweden | `https://www.ogj.com/sweden/rss` | English | Oil/Gas Sweden | To Test | Industry Sweden news |
| Oil & Gas Journal Denmark | `https://www.ogj.com/denmark/rss` | English | Oil/Gas Denmark | To Test | Industry Denmark news |
| Oil & Gas Journal Finland | `https://www.ogj.com/finland/rss` | English | Oil/Gas Finland | To Test | Industry Finland news |
| Oil & Gas Journal Poland | `https://www.ogj.com/poland/rss` | English | Oil/Gas Poland | To Test | Industry Poland news |
| Oil & Gas Journal Czech Republic | `https://www.ogj.com/czech-republic/rss` | English | Oil/Gas Czech Republic | To Test | Industry Czech Republic news |
| Oil & Gas Journal Hungary | `https://www.ogj.com/hungary/rss` | English | Oil/Gas Hungary | To Test | Industry Hungary news |
| Oil & Gas Journal Romania | `https://www.ogj.com/romania/rss` | English | Oil/Gas Romania | To Test | Industry Romania news |
| Oil & Gas Journal Bulgaria | `https://www.ogj.com/bulgaria/rss` | English | Oil/Gas Bulgaria | To Test | Industry Bulgaria news |
| Oil & Gas Journal Croatia | `https://www.ogj.com/croatia/rss` | English | Oil/Gas Croatia | To Test | Industry Croatia news |
| Oil & Gas Journal Slovenia | `https://www.ogj.com/slovenia/rss` | English | Oil/Gas Slovenia | To Test | Industry Slovenia news |
| Oil & Gas Journal Slovakia | `https://www.ogj.com/slovakia/rss` | English | Oil/Gas Slovakia | To Test | Industry Slovakia news |
| Oil & Gas Journal Estonia | `https://www.ogj.com/estonia/rss` | English | Oil/Gas Estonia | To Test | Industry Estonia news |
| Oil & Gas Journal Latvia | `https://www.ogj.com/latvia/rss` | English | Oil/Gas Latvia | To Test | Industry Latvia news |
| Oil & Gas Journal Lithuania | `https://www.ogj.com/lithuania/rss` | English | Oil/Gas Lithuania | To Test | Industry Lithuania news |
| Oil & Gas Journal Greece | `https://www.ogj.com/greece/rss` | English | Oil/Gas Greece | To Test | Industry Greece news |
| Oil & Gas Journal Cyprus | `https://www.ogj.com/cyprus/rss` | English | Oil/Gas Cyprus | To Test | Industry Cyprus news |
| Oil & Gas Journal Malta | `https://www.ogj.com/malta/rss` | English | Oil/Gas Malta | To Test | Industry Malta news |
| Oil & Gas Journal Luxembourg | `https://www.ogj.com/luxembourg/rss` | English | Oil/Gas Luxembourg | To Test | Industry Luxembourg news |
| Oil & Gas Journal Ireland | `https://www.ogj.com/ireland/rss` | English | Oil/Gas Ireland | To Test | Industry Ireland news |
| Oil & Gas Journal Portugal | `https://www.ogj.com/portugal/rss` | English | Oil/Gas Portugal | To Test | Industry Portugal news |
| Oil & Gas Journal Iceland | `https://www.ogj.com/iceland/rss` | English | Oil/Gas Iceland | To Test | Industry Iceland news |
| Oil & Gas Journal Liechtenstein | `https://www.ogj.com/liechtenstein/rss` | English | Oil/Gas Liechtenstein | To Test | Industry Liechtenstein news |
| Oil & Gas Journal Monaco | `https://www.ogj.com/monaco/rss` | English | Oil/Gas Monaco | To Test | Industry Monaco news |
| Oil & Gas Journal San Marino | `https://www.ogj.com/san-marino/rss` | English | Oil/Gas San Marino | To Test | Industry San Marino news |
| Oil & Gas Journal Vatican | `https://www.ogj.com/vatican/rss` | English | Oil/Gas Vatican | To Test | Industry Vatican news |
| Oil & Gas Journal Andorra | `https://www.ogj.com/andorra/rss` | English | Oil/Gas Andorra | To Test | Industry Andorra news |
| Oil & Gas Journal Gibraltar | `https://www.ogj.com/gibraltar/rss` | English | Oil/Gas Gibraltar | To Test | Industry Gibraltar news |
| Oil & Gas Journal Faroe Islands | `https://www.ogj.com/faroe-islands/rss` | English | Oil/Gas Faroe Islands | To Test | Industry Faroe Islands news |
| Oil & Gas Journal Greenland | `https://www.ogj.com/greenland/rss` | English | Oil/Gas Greenland | To Test | Industry Greenland news |
| Oil & Gas Journal Svalbard | `https://www.ogj.com/svalbard/rss` | English | Oil/Gas Svalbard | To Test | Industry Svalbard news |
| Oil & Gas Journal Jan Mayen | `https://www.ogj.com/jan-mayen/rss` | English | Oil/Gas Jan Mayen | To Test | Industry Jan Mayen news |
| Oil & Gas Journal Bouvet Island | `https://www.ogj.com/bouvet-island/rss` | English | Oil/Gas Bouvet Island | To Test | Industry Bouvet Island news |
| Oil & Gas Journal Peter I Island | `https://www.ogj.com/peter-i-island/rss` | English | Oil/Gas Peter I Island | To Test | Industry Peter I Island news |
| Oil & Gas Journal Queen Maud Land | `https://www.ogj.com/queen-maud-land/rss` | English | Oil/Gas Queen Maud Land | To Test | Industry Queen Maud Land news |
| Oil & Gas Journal Ross Dependency | `https://www.ogj.com/ross-dependency/rss` | English | Oil/Gas Ross Dependency | To Test | Industry Ross Dependency news |
| Oil & Gas Journal Australian Antarctic Territory | `https://www.ogj.com/australian-antarctic-territory/rss` | English | Oil/Gas Australian Antarctic Territory | To Test | Industry Australian Antarctic Territory news |
| Oil & Gas Journal Adélie Land | `https://www.ogj.com/adelie-land/rss` | English | Oil/Gas Adélie Land | To Test | Industry Adélie Land news |
| Oil & Gas Journal Chilean Antarctic Territory | `https://www.ogj.com/chilean-antarctic-territory/rss` | English | Oil/Gas Chilean Antarctic Territory | To Test | Industry Chilean Antarctic Territory news |
| Oil & Gas Journal Argentine Antarctica | `https://www.ogj.com/argentine-antarctica/rss` | English | Oil/Gas Argentine Antarctica | To Test | Industry Argentine Antarctica news |
| Oil & Gas Journal British Antarctic Territory | `https://www.ogj.com/british-antarctic-territory/rss` | English | Oil/Gas British Antarctic Territory | To Test | Industry British Antarctic Territory news |
| Oil & Gas Journal French Southern and Antarctic Lands | `https://www.ogj.com/french-southern-and-antarctic-lands/rss` | English | Oil/Gas French Southern and Antarctic Lands | To Test | Industry French Southern and Antarctic Lands news |
| Oil & Gas Journal Heard Island and McDonald Islands | `https://www.ogj.com/heard-island-and-mcdonald-islands/rss` | English | Oil/Gas Heard Island and McDonald Islands | To Test | Industry Heard Island and McDonald Islands news |
| Oil & Gas Journal South Georgia and the South Sandwich Islands | `https://www.ogj.com/south-georgia-and-the-south-sandwich-islands/rss` | English | Oil/Gas South Georgia and the South Sandwich Islands | To Test | Industry South Georgia and the South Sandwich Islands news |
| Oil & Gas Journal French Polynesia | `https://www.ogj.com/french-polynesia/rss` | English | Oil/Gas French Polynesia | To Test | Industry French Polynesia news |
| Oil & Gas Journal New Caledonia | `https://www.ogj.com/new-caledonia/rss` | English | Oil/Gas New Caledonia | To Test | Industry New Caledonia news |
| Oil & Gas Journal Wallis and Futuna | `https://www.ogj.com/wallis-and-futuna/rss` | English | Oil/Gas Wallis and Futuna | To Test | Industry Wallis and Futuna news |
| Oil & Gas Journal Clipperton Island | `https://www.ogj.com/clipperton-island/rss` | English | Oil/Gas Clipperton Island | To Test | Industry Clipperton Island news |
| Oil & Gas Journal Saint Pierre and Miquelon | `https://www.ogj.com/saint-pierre-and-miquelon/rss` | English | Oil/Gas Saint Pierre and Miquelon | To Test | Industry Saint Pierre and Miquelon news |
| Oil & Gas Journal Saint Barthélemy | `https://www.ogj.com/saint-barthelemy/rss` | English | Oil/Gas Saint Barthélemy | To Test | Industry Saint Barthélemy news |
| Oil & Gas Journal Saint Martin | `https://www.ogj.com/saint-martin/rss` | English | Oil/Gas Saint Martin | To Test | Industry Saint Martin news |
| Oil & Gas Journal Guadeloupe | `https://www.ogj.com/guadeloupe/rss` | English | Oil/Gas Guadeloupe | To Test | Industry Guadeloupe news |
| Oil & Gas Journal Martinique | `https://www.ogj.com/martinique/rss` | English | Oil/Gas Martinique | To Test | Industry Martinique news |
| Oil & Gas Journal French Guiana | `https://www.ogj.com/french-guiana/rss` | English | Oil/Gas French Guiana | To Test | Industry French Guiana news |
| Oil & Gas Journal Réunion | `https://www.ogj.com/reunion/rss` | English | Oil/Gas Réunion | To Test | Industry Réunion news |
| Oil & Gas Journal Mayotte | `https://www.ogj.com/mayotte/rss` | English | Oil/Gas Mayotte | To Test | Industry Mayotte news |
| Oil & Gas Journal Saint Helena | `https://www.ogj.com/saint-helena/rss` | English | Oil/Gas Saint Helena | To Test | Industry Saint Helena news |
| Oil & Gas Journal Ascension Island | `https://www.ogj.com/ascension-island/rss` | English | Oil/Gas Ascension Island | To Test | Industry Ascension Island news |
| Oil & Gas Journal Tristan da Cunha | `https://www.ogj.com/tristan-da-cunha/rss` | English | Oil/Gas Tristan da Cunha | To Test | Industry Tristan da Cunha news |
| Oil & Gas Journal Falkland Islands | `https://www.ogj.com/falkland-islands/rss` | English | Oil/Gas Falkland Islands | To Test | Industry Falkland Islands news |
| Oil & Gas Journal South Georgia and the South Sandwich Islands | `https://www.ogj.com/south-georgia-and-the-south-sandwich-islands/rss` | English | Oil/Gas South Georgia and the South Sandwich Islands | To Test | Industry South Georgia and the South Sandwich Islands news |
| Oil & Gas Journal British Antarctic Territory | `https://www.ogj.com/british-antarctic-territory/rss` | English | Oil/Gas British Antarctic Territory | To Test | Industry British Antarctic Territory news |
| Oil & Gas Journal Pitcairn Islands | `https://www.ogj.com/pitcairn-islands/rss` | English | Oil/Gas Pitcairn Islands | To Test | Industry Pitcairn Islands news |
| Oil & Gas Journal Norfolk Island | `https://www.ogj.com/norfolk-island/rss` | English | Oil/Gas Norfolk Island | To Test | Industry Norfolk Island news |
| Oil & Gas Journal Christmas Island | `https://www.ogj.com/christmas-island/rss` | English | Oil/Gas Christmas Island | To Test | Industry Christmas Island news |
| Oil & Gas Journal Cocos Islands | `https://www.ogj.com/cocos-islands/rss` | English | Oil/Gas Cocos Islands | To Test | Industry Cocos Islands news |
| Oil & Gas Journal Ashmore and Cartier Islands | `https://www.ogj.com/ashmore-and-cartier-islands/rss` | English | Oil/Gas Ashmore and Cartier Islands | To Test | Industry Ashmore and Cartier Islands news |
| Oil & Gas Journal Coral Sea Islands | `https://www.ogj.com/coral-sea-islands/rss` | English | Oil/Gas Coral Sea Islands | To Test | Industry Coral Sea Islands news |
| Oil & Gas Journal Heard Island and McDonald Islands | `https://www.ogj.com/heard-island-and-mcdonald-islands/rss` | English | Oil/Gas Heard Island and McDonald Islands | To Test | Industry Heard Island and McDonald Islands news |
| Oil & Gas Journal Australian Antarctic Territory | `https://www.ogj.com/australian-antarctic-territory/rss` | English | Oil/Gas Australian Antarctic Territory | To Test | Industry Australian Antarctic Territory news |
| Oil & Gas Journal Ross Dependency | `https://www.ogj.com/ross-dependency/rss` | English | Oil/Gas Ross Dependency | To Test | Industry Ross Dependency news |
| Oil & Gas Journal Queen Maud Land | `https://www.ogj.com/queen-maud-land/rss` | English | Oil/Gas Queen Maud Land | To Test | Industry Queen Maud Land news |
| Oil & Gas Journal Peter I Island | `https://www.ogj.com/peter-i-island/rss` | English | Oil/Gas Peter I Island | To Test | Industry Peter I Island news |
| Oil & Gas Journal Bouvet Island | `https://www.ogj.com/bouvet-island/rss` | English | Oil/Gas Bouvet Island | To Test | Industry Bouvet Island news |
| Oil & Gas Journal Svalbard | `https://www.ogj.com/svalbard/rss` | English | Oil/Gas Svalbard | To Test | Industry Svalbard news |
| Oil & Gas Journal Jan Mayen | `https://www.ogj.com/jan-mayen/rss` | English | Oil/Gas Jan Mayen | To Test | Industry Jan Mayen news |
| Oil & Gas Journal Greenland | `https://www.ogj.com/greenland/rss` | English | Oil/Gas Greenland | To Test | Industry Greenland news |
| Oil & Gas Journal Faroe Islands | `https://www.ogj.com/faroe-islands/rss` | English | Oil/Gas Faroe Islands | To Test | Industry Faroe Islands news |
| Oil & Gas Journal Gibraltar | `https://www.ogj.com/gibraltar/rss` | English | Oil/Gas Gibraltar | To Test | Industry Gibraltar news |
| Oil & Gas Journal Andorra | `https://www.ogj.com/andorra/rss` | English | Oil/Gas Andorra | To Test | Industry Andorra news |
| Oil & Gas Journal Vatican | `https://www.ogj.com/vatican/rss` | English | Oil/Gas Vatican | To Test | Industry Vatican news |
| Oil & Gas Journal San Marino | `https://www.ogj.com/san-marino/rss` | English | Oil/Gas San Marino | To Test | Industry San Marino news |
| Oil & Gas Journal Monaco | `https://www.ogj.com/monaco/rss` | English | Oil/Gas Monaco | To Test | Industry Monaco news |
| Oil & Gas Journal Liechtenstein | `https://www.ogj.com/liechtenstein/rss` | English | Oil/Gas Liechtenstein | To Test | Industry Liechtenstein news |
| Oil & Gas Journal Iceland | `https://www.ogj.com/iceland/rss` | English | Oil/Gas Iceland | To Test | Industry Iceland news |
| Oil & Gas Journal Portugal | `https://www.ogj.com/portugal/rss` | English | Oil/Gas Portugal | To Test | Industry Portugal news |
| Oil & Gas Journal Ireland | `https://www.ogj.com/ireland/rss` | English | Oil/Gas Ireland | To Test | Industry Ireland news |
| Oil & Gas Journal Luxembourg | `https://www.ogj.com/luxembourg/rss` | English | Oil/Gas Luxembourg | To Test | Industry Luxembourg news |
| Oil & Gas Journal Malta | `https://www.ogj.com/malta/rss` | English | Oil/Gas Malta | To Test | Industry Malta news |
| Oil & Gas Journal Cyprus | `https://www.ogj.com/cyprus/rss` | English | Oil/Gas Cyprus | To Test | Industry Cyprus news |
| Oil & Gas Journal Greece | `https://www.ogj.com/greece/rss` | English | Oil/Gas Greece | To Test | Industry Greece news |
| Oil & Gas Journal Lithuania | `https://www.ogj.com/lithuania/rss` | English | Oil/Gas Lithuania | To Test | Industry Lithuania news |
| Oil & Gas Journal Latvia | `https://www.ogj.com/latvia/rss` | English | Oil/Gas Latvia | To Test | Industry Latvia news |
| Oil & Gas Journal Estonia | `https://www.ogj.com/estonia/rss` | English | Oil/Gas Estonia | To Test | Industry Estonia news |
| Oil & Gas Journal Slovakia | `https://www.ogj.com/slovakia/rss` | English | Oil/Gas Slovakia | To Test | Industry Slovakia news |
| Oil & Gas Journal Slovenia | `https://www.ogj.com/slovenia/rss` | English | Oil/Gas Slovenia | To Test | Industry Slovenia news |
| Oil & Gas Journal Croatia | `https://www.ogj.com/croatia/rss` | English | Oil/Gas Croatia | To Test | Industry Croatia news |
| Oil & Gas Journal Bulgaria | `https://www.ogj.com/bulgaria/rss` | English | Oil/Gas Bulgaria | To Test | Industry Bulgaria news |
| Oil & Gas Journal Romania | `https://www.ogj.com/romania/rss` | English | Oil/Gas Romania | To Test | Industry Romania news |
| Oil & Gas Journal Hungary | `https://www.ogj.com/hungary/rss` | English | Oil/Gas Hungary | To Test | Industry Hungary news |
| Oil & Gas Journal Czech Republic | `https://www.ogj.com/czech-republic/rss` | English | Oil/Gas Czech Republic | To Test | Industry Czech Republic news |
| Oil & Gas Journal Poland | `https://www.ogj.com/poland/rss` | English | Oil/Gas Poland | To Test | Industry Poland news |
| Oil & Gas Journal Finland | `https://www.ogj.com/finland/rss` | English | Oil/Gas Finland | To Test | Industry Finland news |
| Oil & Gas Journal Denmark | `https://www.ogj.com/denmark/rss` | English | Oil/Gas Denmark | To Test | Industry Denmark news |
| Oil & Gas Journal Sweden | `https://www.ogj.com/sweden/rss` | English | Oil/Gas Sweden | To Test | Industry Sweden news |
| Oil & Gas Journal Austria | `https://www.ogj.com/austria/rss` | English | Oil/Gas Austria | To Test | Industry Austria news |
| Oil & Gas Journal Switzerland | `https://www.ogj.com/switzerland/rss` | English | Oil/Gas Switzerland | To Test | Industry Switzerland news |
| Oil & Gas Journal Belgium | `https://www.ogj.com/belgium/rss` | English | Oil/Gas Belgium | To Test | Industry Belgium news |
| Oil & Gas Journal Netherlands | `https://www.ogj.com/netherlands/rss` | English | Oil/Gas Netherlands | To Test | Industry Netherlands news |
| Oil & Gas Journal Spain | `https://www.ogj.com/spain/rss` | English | Oil/Gas Spain | To Test | Industry Spain news |
| Oil & Gas Journal Italy | `https://www.ogj.com/italy/rss` | English | Oil/Gas Italy | To Test | Industry Italy news |
| Oil & Gas Journal France | `https://www.ogj.com/france/rss` | English | Oil/Gas France | To Test | Industry France news |
| Oil & Gas Journal Germany | `https://www.ogj.com/germany/rss` | English | Oil/Gas Germany | To Test | Industry Germany news |
| Oil & Gas Journal UK | `https://www.ogj.com/uk/rss` | English | Oil/Gas UK | To Test | Industry UK news |
| Oil & Gas Journal Norway | `https://www.ogj.com/norway/rss` | English | Oil/Gas Norway | To Test | Industry Norway news |
| Oil & Gas Journal Mexico | `https://www.ogj.com/mexico/rss` | English | Oil/Gas Mexico | To Test | Industry Mexico news |
| Oil & Gas Journal Canada | `https://www.ogj.com/canada/rss` | English | Oil/Gas Canada | To Test | Industry Canada news |
| Oil & Gas Journal Brazil | `https://www.ogj.com/brazil/rss` | English | Oil/Gas Brazil | To Test | Industry Brazil news |
| Oil & Gas Journal India | `https://www.ogj.com/india/rss` | English | Oil/Gas India | To Test | Industry India news |
| Oil & Gas Journal China | `https://www.ogj.com/china/rss` | English | Oil/Gas China | To Test | Industry China news |
| Oil & Gas Journal Russia | `https://www.ogj.com/russia/rss` | English | Oil/Gas Russia | To Test | Industry Russia news |
| Oil & Gas Journal Latin America | `https://www.ogj.com/latin-america/rss` | English | Oil/Gas Latin America | To Test | Industry Latin America news |
| Oil & Gas Journal Africa | `https://www.ogj.com/africa/rss` | English | Oil/Gas Africa | To Test | Industry Africa news |
| Oil & Gas Journal Middle East | `https://www.ogj.com/middle-east/rss` | English | Oil/Gas Middle East | To Test | Industry Middle East news |
| Oil & Gas Journal Asia | `https://www.ogj.com/asia/rss` | English | Oil/Gas Asia | To Test | Industry Asia news |
| Oil & Gas Journal Europe | `https://www.ogj.com/europe/rss` | English | Oil/Gas Europe | To Test | Industry Europe news |
| Oil & Gas Journal North America | `https://www.ogj.com/north-america/rss` | English | Oil/Gas North America | To Test | Industry North America news |
| Oil & Gas Journal International | `https://www.ogj.com/international/rss` | English | Oil/Gas International | To Test | Industry international news |
| Oil & Gas Journal Legal | `https://www.ogj.com/legal/rss` | English | Oil/Gas Legal | To Test | Industry legal news |
| Oil & Gas Journal Finance | `https://www.ogj.com/finance/rss` | English | Oil/Gas Finance | To Test | Industry finance news |
| Oil & Gas Journal Regulations | `https://www.ogj.com/regulations/rss` | English | Oil/Gas Regulations | To Test | Industry regulations news |
| Oil & Gas Journal Safety | `https://www.ogj.com/safety/rss` | English | Oil/Gas Safety | To Test | Industry safety news |
| Oil & Gas Journal Environment | `https://www.ogj.com/environment/rss` | English | Oil/Gas Environment | To Test | Industry environment news |
| Oil & Gas Journal Petrochemicals | `https://www.ogj.com/petrochemicals/rss` | English | Oil/Gas Petrochemicals | To Test | Industry petrochemicals news |
| Oil & Gas Journal Refining | `https://www.ogj.com/refining/rss` | English | Oil/Gas Refining | To Test | Industry refining news |
| Oil & Gas Journal Production | `https://www.ogj.com/production/rss` | English | Oil/Gas Production | To Test | Industry production news |
| Oil & Gas Journal Exploration | `https://www.ogj.com/exploration/rss` | English | Oil/Gas Exploration | To Test | Industry exploration news |
| Oil & Gas Journal Operations | `https://www.ogj.com/operations/rss` | English | Oil/Gas Operations | To Test | Industry operations news |
| Oil & Gas Journal Markets | `https://www.ogj.com/markets/rss` | English | Oil/Gas Markets | To Test | Industry market news |
| Oil & Gas Journal Technology | `https://www.ogj.com/technology/rss` | English | Oil/Gas Technology | To Test | Industry technology news |
| Oil & Gas Journal Business | `https://www.ogj.com/business/rss` | English | Oil/Gas Business | To Test | Industry business news |
| Platts | `https://www.spglobal.com/platts/en/rss` | English | Commodities | To Test | Commodities data |
| Argus Media | `https://www.argusmedia.com/rss` | English | Commodities | To Test | Energy commodities |
| Energy Voice | `https://www.energyvoice.com/rss/` | English | Energy | To Test | Global energy news |
| World Oil | `https://www.worldoil.com/rss/` | English | Oil | To Test | Oil industry |
| Rigzone | `https://www.rigzone.com/rss/` | English | Oil/Gas | To Test | Oil & gas industry |

## Testing Methodology

### Phase 1: RSS Feed Testing
For each RSS feed, test:
1. **Accessibility**: Can we fetch the feed without errors?
2. **Format**: Is it valid RSS/Atom XML?
3. **Content**: Does it contain recent articles?
4. **Relevance**: Do articles match our keywords (energy, AI, blockchain)?
5. **Geographic**: Are articles from target regions?
6. **Rate Limiting**: How many requests can we make?

### Phase 2: Direct Scraping Testing
For each direct scraping source, test:
1. **Accessibility**: Can we access the main page?
2. **Article Discovery**: Can we find article links?
3. **Content Extraction**: Can we extract full article content?
4. **Rate Limiting**: How many requests can we make?
5. **Anti-Bot Measures**: Any blocking or CAPTCHAs?

### Phase 3: Geographic Tagging Testing
Test the enhanced geographic detection:
1. **City Detection**: Can we detect cities from new regions?
2. **Country Detection**: Can we detect countries from new regions?
3. **Continent Mapping**: Are articles properly tagged with continents?
4. **False Positives**: Are we avoiding incorrect geographic assignments?

## Implementation Steps

### Step 1: RSS Feed Testing Script
Create a test script that:
- Tests each RSS feed URL
- Validates XML format
- Checks for recent articles
- Measures response times
- **Only includes sources that pass ALL tests**
- Logs results to a file

### Step 2: Direct Scraping Testing Script
Create a test script that:
- Tests each direct scraping URL
- Attempts to find article links
- Tests content extraction
- **Only includes sources that pass ALL tests**
- Logs results to a file

### Step 3: Geographic Detection Testing
Create a test script that:
- Tests geographic detection on sample articles
- Validates continent assignments
- Checks for false positives/negatives
- Measures accuracy

### Step 4: Integration Testing
Test the full scraper with new sources:
- Run scraper with new sources
- Measure article collection rates
- Validate geographic distribution
- **Remove any sources that cause errors or fail during integration**
- Only deploy sources that work reliably in production

## Success Metrics

### Quantitative Metrics
- **Geographic Distribution**: Target 30%+ from Africa, Latam, MENA
- **Source Diversity**: 50+ new sources added
- **Article Volume**: Maintain or increase total article count
- **Success Rate**: 100% of new sources working reliably (no broken sources in production)

### Qualitative Metrics
- **Relevance**: Articles match energy/AI/blockchain keywords
- **Recency**: Articles are from past 24 hours
- **Quality**: Articles have substantial content
- **Diversity**: Good mix of regions and topics

## Risk Mitigation

### Technical Risks
- **Source Reliability**: Test thoroughly before adding - **ONLY include 100% working sources**
- **Rate Limiting**: Implement proper delays
- **Anti-Bot Measures**: Use proper headers and rotation
- **Content Extraction**: Test extraction methods
- **Broken Source Pollution**: Remove any sources that stop working to maintain system reliability

### Content Risks
- **Language Barriers**: Focus on English sources initially
- **Cultural Context**: Ensure content is relevant
- **Political Sensitivity**: Avoid controversial sources
- **Quality Control**: Filter out low-quality content

## Timeline

### Week 1: RSS Feed Testing
- Test all proposed RSS feeds
- Document working feeds
- Identify issues and solutions

### Week 2: Direct Scraping Testing
- Test all proposed direct scraping sources
- Document working sources
- Refine extraction methods

### Week 3: Integration and Testing
- Integrate working sources into scraper
- Test full system
- Measure improvements

### Week 4: Optimization and Deployment
- Optimize performance
- Deploy to production
- Monitor results

## Next Steps

1. **Approve this plan** and any modifications
2. **Create testing scripts** for systematic validation
3. **Begin RSS feed testing** with the proposed sources
4. **Iterate based on results** and refine the approach
5. **Implement working sources** into the production scraper

---

**This plan provides a systematic approach to improving geographic coverage while maintaining quality and reliability. Please review and let me know if you'd like any modifications or additional details.**