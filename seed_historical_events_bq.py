# seed_historical_events_bq.py
import os
import sys
from dotenv import load_dotenv
import vertexai
from vertexai.language_models import TextEmbeddingModel
from google.cloud import bigquery

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION", "us-central1")

if not PROJECT_ID:
    print("Error: GCP_PROJECT_ID not set in .env")
    sys.exit(1)

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=REGION)
embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-005")

# Initialize BigQuery Client
bq_client = bigquery.Client(project=PROJECT_ID)
DATASET_ID = "de_intel_dataset"
TABLE_ID = "historical_events"
FULL_TABLE_REF = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Reuse the 50 historical events from the previous configuration
HISTORICAL_EVENTS_CORPUS = [
    {
        "id": "hist_1979_iran_oil_crisis",
        "title": "1979 Iranian Revolution & Oil Crisis",
        "date": "1979-01-16",
        "sector": "Geopolitical, Market/Financial, Supply Chain",
        "description": "The Iranian Revolution led to a massive disruption of the global oil supply. Panic buying drove crude prices to more than double, triggering global inflation and a major economic recession in Western countries.",
        "outcome": "Western nations shifted toward strategic petroleum reserves (SPR), energy conservation, and diversification of oil supplies away from the Middle East."
    },
    {
        "id": "hist_1985_plaza_accord",
        "title": "1985 Plaza Accord Currency Agreement",
        "date": "1985-09-22",
        "sector": "Market/Financial, Regulatory/Policy",
        "description": "G5 nations signed the Plaza Accord to depreciate the US dollar against the Japanese Yen and German Mark to reduce the US trade deficit, triggering massive currency fluctuations.",
        "outcome": "Led to major appreciation of the Yen and contributed significantly to the formation of Japan's asset price bubble in the late 1980s."
    },
    {
        "id": "hist_1987_black_monday",
        "title": "1987 Black Monday Stock Market Crash",
        "date": "1987-10-19",
        "sector": "Market/Financial",
        "description": "The Dow Jones Industrial Average collapsed by 22.6% in a single day, fueled by panic, structural market issues, and early program trading algorithms.",
        "outcome": "Global exchanges implemented 'circuit breakers' to temporarily halt trading during severe declines to preserve liquidity."
    },
    {
        "id": "hist_1990_gulf_war_invasion",
        "title": "1990 Iraqi Invasion of Kuwait & Oil Shock",
        "date": "1990-08-02",
        "sector": "Geopolitical, Supply Chain",
        "description": "Iraq's sudden invasion of Kuwait halted regional petroleum exports and drove global crude oil prices from $17 to $40 a barrel, sparking economic slowdowns.",
        "outcome": "Coordinated international military response and the solidification of Middle Eastern maritime protection protocols."
    },
    {
        "id": "hist_1992_black_wednesday",
        "title": "1992 Black Wednesday Sterling Collapse",
        "date": "1992-09-16",
        "sector": "Market/Financial",
        "description": "Speculative short-selling forced the British government to withdraw the Pound Sterling from the European Exchange Rate Mechanism (ERM).",
        "outcome": "Devastated the credibility of UK currency defense strategies but ultimately led to a domestic economic boom and interest rate reductions."
    },
    {
        "id": "hist_1994_mexican_peso_crisis",
        "title": "1994 Mexican Peso Devaluation Crisis",
        "date": "1994-12-20",
        "sector": "Market/Financial",
        "description": "The sudden devaluation of the Mexican Peso triggered a severe flight of international capital and threatened sovereign default.",
        "outcome": "Resolved by a $50 billion IMF and US Treasury stabilization package to prevent contagion across Latin America."
    },
    {
        "id": "hist_1997_asian_financial_crisis",
        "title": "1997 Asian Financial Crisis",
        "date": "1997-07-02",
        "sector": "Market/Financial",
        "description": "The collapse of the Thai Baht triggered massive capital flight and asset collapses across Southeast Asia, impacting South Korea, Indonesia, and Hong Kong.",
        "outcome": "Required massive IMF interventions conditional on structural reforms and currency float implementations."
    },
    {
        "id": "hist_1998_russian_default_ltcm",
        "title": "1998 Russian Financial Crisis & LTCM Bailout",
        "date": "1998-08-17",
        "sector": "Market/Financial, Geopolitical",
        "description": "Russia devalued the Ruble and defaulted on its domestic debt, causing systemic shockwaves that nearly collapsed the prominent hedge fund LTCM.",
        "outcome": "A private consortium of major Wall Street banks stepped in to bail out LTCM under Federal Reserve supervision to protect clearing structures."
    },
    {
        "id": "hist_1999_euro_currency_launch",
        "title": "1999 Electronic Launch of the Euro",
        "date": "1999-01-01",
        "sector": "Market/Financial, Regulatory/Policy",
        "description": "The Euro was launched as an accounting currency across 11 European Union countries, centralizing monetary policy under the ECB.",
        "outcome": "Laid structural integration foundations but also exposed severe sovereign debt systemic imbalances in the following decade."
    },
    {
        "id": "hist_2000_dot_com_bubble",
        "title": "2000 Dot-com Tech Bubble Burst",
        "date": "2000-03-10",
        "sector": "Technology, Market/Financial",
        "description": "Speculative investment in overvalued internet startups peaked, leading to a massive tech stock collapse and the bankruptcy of hundreds of firms.",
        "outcome": "Wiped out trillions in market value, leading to market consolidation and a shift toward actual cash flow valuations."
    },
    {
        "id": "hist_2001_argentina_default",
        "title": "2001 Argentina Sovereign Debt Default",
        "date": "2001-12-26",
        "sector": "Market/Financial",
        "description": "Amidst severe depression and capital flight, Argentina defaulted on over $93 billion in sovereign debt, ending the peso-dollar peg.",
        "outcome": "Caused widespread social unrest, banking freezes, and years of international litigation with holdout creditors."
    },
    {
        "id": "hist_2001_september_11",
        "title": "2001 September 11 Terrorist Attacks",
        "date": "2001-09-11",
        "sector": "Geopolitical, Social/Public Sentiment",
        "description": "Al-Qaeda hijackers destroyed the World Trade Center and struck the Pentagon, causing thousands of casualties and halting global aviation.",
        "outcome": "Catalyzed the global 'War on Terror', major geopolitical re-alignments, and sweeping domestic surveillance legislation."
    },
    {
        "id": "hist_2001_enron_collapse",
        "title": "2001 Enron Scandal & Corporate Collapse",
        "date": "2001-12-02",
        "sector": "Regulatory/Policy, Market/Financial",
        "description": "Accounting fraud and systemic mark-to-market manipulation exposed Enron's massive hidden debt, triggering bankruptcy.",
        "outcome": "Led to the dissolution of Arthur Andersen and the passage of the Sarbanes-Oxley Act of 2002 to enforce corporate audit compliance."
    },
    {
        "id": "hist_2002_physical_euro_cash",
        "title": "2002 Physical Introduction of Euro Banknotes",
        "date": "2002-01-01",
        "sector": "Market/Financial, Regulatory/Policy",
        "description": "Physical euro coins and banknotes replaced national currencies across 12 eurozone countries in the largest monetary swap in history.",
        "outcome": "Created a unified physical currency market, accelerating trade and price transparency across Europe."
    },
    {
        "id": "hist_2003_sars_outbreak",
        "title": "2003 SARS Epidemic Outbreak",
        "date": "2003-03-12",
        "sector": "Supply Chain, Social/Public Sentiment",
        "description": "Severe Acute Respiratory Syndrome spread rapidly across Southeast Asia and Canada, disrupting global trade, travel, and operations.",
        "outcome": "Enhanced international epidemiological surveillance networks and highlighted regional supply dependence on East Asia."
    },
    {
        "id": "hist_2003_iraq_invasion",
        "title": "2003 US-led Invasion of Iraq",
        "date": "2003-03-20",
        "sector": "Geopolitical",
        "description": "A US-led military coalition invaded Iraq, overthrew Saddam Hussein's regime, and triggered prolonged regional warfare.",
        "outcome": "Altered the Middle Eastern power balance and led to decades of localized instability and counter-insurgency conflicts."
    },
    {
        "id": "hist_2005_hurricane_katrina",
        "title": "2005 Hurricane Katrina US Levee Breach",
        "date": "2005-08-29",
        "sector": "Supply Chain, Social/Public Sentiment",
        "description": "A Category 5 hurricane breached New Orleans' levee systems, flooding 80% of the city and severely shutting down Gulf Coast petroleum installations.",
        "outcome": "Exposed critical emergency response failures and initiated major engineering overhauls of maritime flood protections."
    },
    {
        "id": "hist_2006_aws_cloud_launch",
        "title": "2006 Launch of Amazon Web Services",
        "date": "2006-03-14",
        "sector": "Technology, Competitive/Industry",
        "description": "Amazon launched AWS (EC2/S3), pioneering commercial cloud infrastructure and drastically reducing digital capital requirements.",
        "outcome": "Enabled the rapid growth of modern web startups and sparked a global enterprise shift to off-premise server architectures."
    },
    {
        "id": "hist_2007_iphone_launch",
        "title": "2007 Launch of the Apple iPhone",
        "date": "2007-06-29",
        "sector": "Technology, Competitive/Industry",
        "description": "Apple launched the first iPhone, initiating the smartphone era and introducing multi-touch consumer mobile computing.",
        "outcome": "Reshaped the technology sector, resulting in the decline of legacy mobile giants like Nokia and BlackBerry, while fostering the mobile app economy."
    },
    {
        "id": "hist_2008_bitcoin_whitepaper",
        "title": "2008 Bitcoin Whitepaper Publication",
        "date": "2008-10-31",
        "sector": "Technology, Market/Financial",
        "description": "Satoshi Nakamoto published the Bitcoin whitepaper, outlining a peer-to-peer decentralized electronic cash system.",
        "outcome": "Laid the cryptographic and conceptual foundations for today's multi-trillion dollar cryptocurrency asset class."
    },
    {
        "id": "hist_2008_lehman_brothers",
        "title": "2008 Lehman Brothers Bankruptcy",
        "date": "2008-09-15",
        "sector": "Market/Financial",
        "description": "Investment bank Lehman Brothers filed for bankruptcy due to massive subprime mortgage exposure, freezing global credit markets.",
        "outcome": "Triggered the Great Recession, requiring systemic central bank interventions, rate cuts, and the Dodd-Frank regulation act."
    },
    {
        "id": "hist_2009_greek_debt_crisis",
        "title": "2009 Greek Sovereign Debt Crisis",
        "date": "2009-10-04",
        "sector": "Market/Financial, Geopolitical",
        "description": "Greece's revised budget deficits sparked a severe debt crisis, threatening the cohesion of the Eurozone and risking fiscal default.",
        "outcome": "Resulted in massive ECB/IMF austerity-linked bailouts and prolonged structural economic contractions in Southern Europe."
    },
    {
        "id": "hist_2010_deepwater_horizon",
        "title": "2010 Deepwater Horizon Oil Spill",
        "date": "2010-04-20",
        "sector": "Regulatory/Policy, Supply Chain",
        "description": "An explosion on BP's Deepwater Horizon offshore rig caused the largest marine oil spill in history within the Gulf of Mexico.",
        "outcome": "Prompted severe new US offshore drilling safety standards, permanent permit adjustments, and billions in environmental damages."
    },
    {
        "id": "hist_2010_flash_crash",
        "title": "2010 High-Frequency Trading Flash Crash",
        "date": "2010-05-06",
        "sector": "Market/Financial, Technology",
        "description": "A rapid $1 trillion US stock crash and recovery occurred in 36 minutes, fueled by algorithmic spoofing and high-frequency trading loops.",
        "outcome": "Highlighted systemic vulnerabilities of automated market dependencies and triggered strict automated trading limits."
    },
    {
        "id": "hist_2011_fukushima_disaster",
        "title": "2011 Fukushima Daiichi Nuclear Meltdown",
        "date": "2011-03-11",
        "sector": "Social/Public Sentiment, Regulatory/Policy, Supply Chain",
        "description": "A major earthquake and subsequent tsunami struck northern Japan, triggering a triple meltdown at the Fukushima Daiichi nuclear plant.",
        "outcome": "Accelerated global shifts away from nuclear power, prompting Germany to shut down all nuclear reactors."
    },
    {
        "id": "hist_2011_arab_spring",
        "title": "2011 Arab Spring Political Uprisings",
        "date": "2011-12-18",
        "sector": "Geopolitical, Social/Public Sentiment",
        "description": "Pro-democracy protests overthrew autocratic regimes in Tunisia, Egypt, and Libya, and catalyzed the Syrian Civil War.",
        "outcome": "Created major geopolitical instability across the region and led to subsequent migrations into Europe."
    },
    {
        "id": "hist_2012_libor_scandal",
        "title": "2012 Libor Interest Rate Manipulation",
        "date": "2012-06-27",
        "sector": "Regulatory/Policy, Market/Financial",
        "description": "Major global banks colluded to manipulate the Libor rate to boost derivative profits and project false financial health.",
        "outcome": "Shook public confidence, led to billions in corporate penalties, and initiated the transition to the SOFR benchmark rate."
    },
    {
        "id": "hist_2013_snowden_leaks",
        "title": "2013 Snowden Global Surveillance Disclosures",
        "date": "2013-06-05",
        "sector": "Technology, Geopolitical, Regulatory/Policy",
        "description": "Edward Snowden leaked classified NSA documents revealing vast international cyber surveillance networks operated in tandem with tech firms.",
        "outcome": "Catalyzed a massive commercial push toward end-to-end encryption and intensified transatlantic diplomatic data privacy disputes."
    },
    {
        "id": "hist_2014_crimea_annexation",
        "title": "2014 Russian Annexation of Crimea",
        "date": "2014-03-18",
        "sector": "Geopolitical",
        "description": "Following political shifts in Ukraine, Russian forces seized and annexed the Crimean Peninsula, violating post-Cold War treaties.",
        "outcome": "Triggered targeted US and EU economic sanctions and initiated a long-term economic pivot by Russia toward China."
    },
    {
        "id": "hist_2014_ebola_epidemic",
        "title": "2014 West African Ebola Epidemic",
        "date": "2014-03-23",
        "sector": "Geopolitical, Social/Public Sentiment",
        "description": "A severe Ebola outbreak swept Guinea, Liberia, and Sierra Leone, threatening regional administrative controls and public health.",
        "outcome": "Prompted large-scale international emergency response teams and led to the acceleration of viral vaccine research."
    },
    {
        "id": "hist_2015_volkswagen_dieselgate",
        "title": "2015 Volkswagen Emissions Fraud Scandal",
        "date": "2015-09-18",
        "sector": "Regulatory/Policy, Competitive/Industry",
        "description": "Regulators discovered Volkswagen had programmed diesel vehicles to activate emission controls only during laboratory compliance tests.",
        "outcome": "Resulted in billions of dollars in fines, executive indictments, and a sector-wide transition to electric vehicle investments."
    },
    {
        "id": "hist_2015_paris_agreement",
        "title": "2015 Paris Climate Accord Signing",
        "date": "2015-12-12",
        "sector": "Regulatory/Policy",
        "description": "Nearly 200 nations signed a binding agreement to limit global warming below 2 degrees Celsius through national emissions targets.",
        "outcome": "Redirected immense global public and private capital into renewable energy and green technologies."
    },
    {
        "id": "hist_2016_brexit_referendum",
        "title": "2016 UK Brexit Referendum Vote",
        "date": "2016-06-23",
        "sector": "Geopolitical, Market/Financial, Regulatory/Policy",
        "description": "The UK unexpectedly voted to exit the European Union, triggering immediate political turmoil and a sharp drop in the value of the Pound.",
        "outcome": "Completed formal EU separation in 2020, restructuring custom borders, immigration policies, and trade networks."
    },
    {
        "id": "hist_2016_trump_election",
        "title": "2016 US Election of Donald Trump",
        "date": "2016-11-08",
        "sector": "Geopolitical, Regulatory/Policy",
        "description": "Donald Trump was elected US president on an protectionist 'America First' platform, challenging existing trade alliances.",
        "outcome": "Led to the renegotiation of NAFTA (into USMCA), US withdrawal from the TPP, and an era of unilateral trade actions."
    },
    {
        "id": "hist_2018_gdpr_enforcement",
        "title": "2018 EU GDPR Privacy Law Enforcement",
        "date": "2018-05-25",
        "sector": "Regulatory/Policy, Technology",
        "description": "The EU's sweeping General Data Protection Regulation took effect, imposing strict privacy, consent, and user data controls.",
        "outcome": "Established a global data standard, forcing tech platforms to restructure consent mechanisms and data storage architectures."
    },
    {
        "id": "hist_2018_us_china_trade_war",
        "title": "2018 US-China Tariff Escalation",
        "date": "2018-07-06",
        "sector": "Geopolitical, Supply Chain",
        "description": "The US began imposing tariffs on billions of dollars of Chinese imports, and China retaliated, initiating a prolonged trade dispute.",
        "outcome": "Disrupted global tech manufacturing and initiated nearshoring trends to countries like Vietnam and Mexico."
    },
    {
        "id": "hist_2018_cambridge_analytica",
        "title": "2018 Cambridge Analytica Data harvesting",
        "date": "2018-03-17",
        "sector": "Technology, Social/Public Sentiment",
        "description": "It was revealed that Cambridge Analytica harvested personal data of millions of Facebook users without consent for political advertising campaigns.",
        "outcome": "Sparked global regulatory investigations, massive public backlash against Big Tech, and historic privacy fines for Facebook."
    },
    {
        "id": "hist_2019_huawei_blacklist",
        "title": "2019 US Entity Blacklisting of Huawei",
        "date": "2019-05-15",
        "sector": "Technology, Geopolitical, Supply Chain",
        "description": "The US placed Huawei on the Entity List, restricting domestic exports to the Chinese telecom firm over national security issues.",
        "outcome": "Disrupted Huawei's supply of chips and software (like Google Mobile Services) and accelerated China's domestic semiconductor research."
    },
    {
        "id": "hist_2020_covid_pandemic",
        "title": "2020 COVID-19 Outbreak & Global Lockdowns",
        "date": "2020-03-11",
        "sector": "Social/Public Sentiment, Supply Chain, Market/Financial",
        "description": "The WHO declared COVID-19 a pandemic, leading to unprecedented peacetime lockdowns, border closures, and business suspensions.",
        "outcome": "Caused a major economic contraction, required trillions in fiscal stimulus, and accelerated remote-work technologies."
    },
    {
        "id": "hist_2020_negative_crude_oil",
        "title": "2020 Negative WTI Crude Oil Price Collapse",
        "date": "2020-04-20",
        "sector": "Market/Financial, Supply Chain",
        "description": "Pandemic demand destruction and an OPEC+ trade dispute led to storage constraints, driving WTI oil futures to negative $37 per barrel.",
        "outcome": "Prompted major OPEC+ production cuts and reduced corporate capital expenditure in new fossil-fuel exploration projects."
    },
    {
        "id": "hist_2021_gamestop_short_squeeze",
        "title": "2021 Retail-Driven GameStop Short Squeeze",
        "date": "2021-01-27",
        "sector": "Market/Financial, Social/Public Sentiment",
        "description": "Retail traders on Reddit coordinated a massive short squeeze of GameStop, causing billions in losses for short-selling hedge funds.",
        "outcome": "Exposed the emerging market influence of retail coalitions and triggered reviews of trading platform liquidity margins."
    },
    {
        "id": "hist_2021_suez_canal_blockage",
        "title": "2021 Suez Canal Blockage by Ever Given",
        "date": "2021-03-23",
        "sector": "Supply Chain",
        "description": "The ultra-large Ever Given container ship wedged across the Suez Canal, halting critical trade between Asia and Europe for six days.",
        "outcome": "Exposed global vulnerabilities in just-in-time logistics and maritime trade bottlenecks, accelerating calls for redundancy."
    },
    {
        "id": "hist_2021_colonial_pipeline_hack",
        "title": "2021 Colonial Pipeline Ransomware Hack",
        "date": "2021-05-07",
        "sector": "Technology, Supply Chain, Regulatory/Policy",
        "description": "A ransomware attack on Colonial Pipeline forced the shutdown of the largest East Coast fuel pipeline, causing regional panic buying.",
        "outcome": "Demonstrated the physical vulnerability of critical utility assets to cyber threats and prompted federal security mandates."
    },
    {
        "id": "hist_2021_el_salvador_bitcoin",
        "title": "2021 El Salvador Bitcoin Legal Tender Law",
        "date": "2021-09-07",
        "sector": "Market/Financial, Regulatory/Policy",
        "description": "El Salvador became the first nation to mandate Bitcoin as legal tender alongside the US Dollar, launching a state-sponsored wallet.",
        "outcome": "Faced severe pushback from the IMF, rating downgrades, and highly mixed domestic adoption due to market volatility."
    },
    {
        "id": "hist_2022_ukraine_invasion",
        "title": "2022 Russian Invasion of Ukraine",
        "date": "2022-02-24",
        "sector": "Geopolitical, Supply Chain, Market/Financial",
        "description": "Russia launched a full-scale invasion of Ukraine, triggering a major European conflict and sparking global grain and energy shocks.",
        "outcome": "Prompted a rapid European pivot away from Russian gas, NATO expansion, and a major upswing in global defense budgets."
    },
    {
        "id": "hist_2022_chips_science_act",
        "title": "2022 US CHIPS and Science Act Signed",
        "date": "2022-08-09",
        "sector": "Regulatory/Policy, Technology, Supply Chain",
        "description": "The US enacted the CHIPS Act, providing $52.7 billion in subsidies to relocate critical advanced semiconductor manufacturing domestically.",
        "outcome": "Accelerated global tech-sovereignty competition, leading to massive domestic microchip plant constructions."
    },
    {
        "id": "hist_2022_ftx_exchange_collapse",
        "title": "2022 FTX Crypto Exchange Bankruptcy",
        "date": "2022-11-11",
        "sector": "Market/Financial, Regulatory/Policy",
        "description": "FTX collapsed into insolvency following reports that client funds were diverted to Alameda Research, wiping out billions.",
        "outcome": "Triggered systemic crypto liquidations, intense global regulatory oversight, and corporate fraud convictions."
    },
    {
        "id": "hist_2023_svb_liquidity_failure",
        "title": "2023 Silicon Valley Bank Liquidity Run",
        "date": "2023-03-10",
        "sector": "Market/Financial, Regulatory/Policy",
        "description": "A bank run triggered by paper losses on low-yield US Treasury holdings collapsed Silicon Valley Bank, threatening regional banking liquidity.",
        "outcome": "Prompted emergency deposit guarantees by the FDIC and the creation of Fed lending facilities to secure mid-sized bank reserves."
    },
    {
        "id": "hist_2023_chatgpt_explosion",
        "title": "2023 Mass Enterprise Adoption of Generative AI",
        "date": "2023-01-30",
        "sector": "Technology, Competitive/Industry",
        "description": "OpenAI's ChatGPT recorded historic adoption rates, initiating an enterprise software race and massive AI infrastructure spending.",
        "outcome": "Drove Nvidia to record valuations, triggered global AI safety bills, and initiated wide-scale corporate automation."
    },
    {
        "id": "hist_2024_crowdstrike_it_outage",
        "title": "2024 CrowdStrike Global Software IT Outage",
        "date": "2024-07-19",
        "sector": "Technology, Supply Chain",
        "description": "A faulty software update deployed by CrowdStrike crashed millions of Windows systems, halting air travel, shipping, and banking.",
        "outcome": "Exposed the systemic vulnerability of global dependence on highly centralized SaaS monocultures, prioritizing recovery redundancies."
    }
]

def create_dataset_and_table():
    # 1. Create Dataset
    dataset = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    dataset.location = REGION
    try:
        bq_client.create_dataset(dataset, exists_ok=True)
        print(f"Dataset {DATASET_ID} confirmed in BigQuery.")
    except Exception as e:
        print(f"Error creating dataset: {e}")

    # 2. Define Table Schema with Vector Column
    schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("date", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("sector", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("outcome", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),  # Array of floats
    ]
    
    table = bigquery.Table(FULL_TABLE_REF, schema=schema)
    try:
        bq_client.create_table(table, exists_ok=True)
        print(f"Table {TABLE_ID} confirmed in BigQuery.")
    except Exception as e:
        print(f"Error creating table: {e}")

def main():
    create_dataset_and_table()
    
    print(f"Generating vectors via Vertex AI text-embedding-005 and inserting to BigQuery...")
    rows_to_insert = []
    
    for i, event in enumerate(HISTORICAL_EVENTS_CORPUS):
        doc_text = f"Title: {event['title']} | Date: {event['date']} | Description: {event['description']} | Outcome: {event['outcome']}"
        print(f"[{i+1}/{len(HISTORICAL_EVENTS_CORPUS)}] Embedding: {event['title']}...")
        
        try:
            # Generate Embedding using Vertex AI[<vertex-ai-rich-citation-chip>3</vertex-ai-rich-citation-chip>]
            embeddings = embedding_model.get_embeddings([doc_text])
            vector = embeddings[0] .values
            
            rows_to_insert.append({
                "id": event["id"],
                "title": event["title"],
                "date": event["date"],
                "sector": event["sector"],
                "description": event["description"],
                "outcome": event["outcome"],
                "embedding": vector
            })
        except Exception as e:
            print(f"Failed embedding of event {event['title']}: {e}")
            sys.exit(1)
            
    # Perform streaming insertion
    errors = bq_client.insert_rows_json(FULL_TABLE_REF, rows_to_insert)
    if errors:
        print(f"Insertion errors encountered: {errors}")
    else:
        print(f"Seeding completed successfully! BigQuery populated with {len(HISTORICAL_EVENTS_CORPUS)} events.")

if __name__ == "__main__":
    main()