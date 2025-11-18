import streamlit as st
import json
import os
from datetime import datetime
import hashlib
import io

# Translation imports
import argostranslate.package
import argostranslate.translate
from argostranslate.tags import translate_tags

# TTS imports
from gtts import gTTS

# Initialize session state
def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'all_languages' not in st.session_state:
        st.session_state.all_languages = []
    if 'installed_languages' not in st.session_state:
        st.session_state.installed_languages = []

class UserManager:
    def __init__(self, users_file='users.json'):
        self.users_file = users_file
        self.load_users()
    
    def load_users(self):
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            else:
                self.users = {}
        except Exception:
            self.users = {}
    
    def save_users(self):
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=4)
            return True
        except Exception:
            return False
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password):
        if username.strip() == "":
            return False, "Username cannot be empty"
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(password) < 3:
            return False, "Password must be at least 3 characters"
        if username in self.users:
            return False, "Username already exists"
        
        self.users[username] = {
            'password': self.hash_password(password),
            'history': [],
            'created_at': datetime.now().isoformat()
        }
        if self.save_users():
            return True, "User created successfully"
        return False, "Error saving user data"
    
    def login(self, username, password):
        if username in self.users and self.users[username]['password'] == self.hash_password(password):
            return True, "Login successful"
        return False, "Invalid username or password"
    
    def get_user_history(self, username):
        return self.users.get(username, {}).get('history', [])
    
    def save_user_history(self, username, history_item):
        if username in self.users:
            history = self.users[username].get('history', [])
            history.insert(0, history_item)
            # Keep only last 10 items
            if len(history) > 10:
                history = history[:10]
            self.users[username]['history'] = history
            return self.save_users()
        return False

class TranslationManager:
    def __init__(self):
        self.load_languages()
    
    def load_languages(self):
        """Load all available languages from Argos Translate"""
        try:
            # Get installed packages
            installed_packages = argostranslate.package.get_installed_packages()
            installed_languages = set()
            
            for pkg in installed_packages:
                installed_languages.add(pkg.from_code)
                installed_languages.add(pkg.to_code)
            
            st.session_state.installed_languages = sorted(list(installed_languages))
            
            # Define 1000+ languages with their codes and names
            all_languages = {
                'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German', 
                'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
                'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic', 'hi': 'Hindi',
                'bn': 'Bengali', 'pa': 'Punjabi', 'te': 'Telugu', 'mr': 'Marathi',
                'ta': 'Tamil', 'ur': 'Urdu', 'gu': 'Gujarati', 'kn': 'Kannada',
                'or': 'Odia', 'ml': 'Malayalam', 'sa': 'Sanskrit', 'ne': 'Nepali',
                'si': 'Sinhala', 'my': 'Burmese', 'km': 'Khmer', 'th': 'Thai',
                'lo': 'Lao', 'vi': 'Vietnamese', 'id': 'Indonesian', 'ms': 'Malay',
                'tl': 'Tagalog', 'jw': 'Javanese', 'su': 'Sundanese', 'ceb': 'Cebuano',
                'tr': 'Turkish', 'fa': 'Persian', 'ps': 'Pashto', 'ku': 'Kurdish',
                'he': 'Hebrew', 'yi': 'Yiddish', 'am': 'Amharic', 'ti': 'Tigrinya',
                'om': 'Oromo', 'so': 'Somali', 'sw': 'Swahili', 'rw': 'Kinyarwanda',
                'lg': 'Luganda', 'yo': 'Yoruba', 'ig': 'Igbo', 'ha': 'Hausa',
                'ff': 'Fulah', 'sn': 'Shona', 'xh': 'Xhosa', 'zu': 'Zulu',
                'af': 'Afrikaans', 'nl': 'Dutch', 'sv': 'Swedish', 'no': 'Norwegian',
                'da': 'Danish', 'fi': 'Finnish', 'et': 'Estonian', 'lv': 'Latvian',
                'lt': 'Lithuanian', 'pl': 'Polish', 'cs': 'Czech', 'sk': 'Slovak',
                'hu': 'Hungarian', 'ro': 'Romanian', 'bg': 'Bulgarian', 'el': 'Greek',
                'mk': 'Macedonian', 'sq': 'Albanian', 'hr': 'Croatian', 'sr': 'Serbian',
                'sl': 'Slovenian', 'bs': 'Bosnian', 'mt': 'Maltese', 'ga': 'Irish',
                'gd': 'Scottish Gaelic', 'cy': 'Welsh', 'br': 'Breton', 'is': 'Icelandic',
                'fo': 'Faroese', 'ca': 'Catalan', 'gl': 'Galician', 'eu': 'Basque',
                'oc': 'Occitan', 'sc': 'Sardinian', 'co': 'Corsican', 'fur': 'Friulian',
                'ast': 'Asturian', 'an': 'Aragonese', 'tt': 'Tatar', 'ba': 'Bashkir',
                'crh': 'Crimean Tatar', 'krc': 'Karachay-Balkar', 'ka': 'Georgian',
                'hy': 'Armenian', 'az': 'Azerbaijani', 'tk': 'Turkmen', 'uz': 'Uzbek',
                'kk': 'Kazakh', 'ky': 'Kyrgyz', 'ug': 'Uyghur', 'mn': 'Mongolian',
                'bo': 'Tibetan', 'dz': 'Dzongkha', 'new': 'Newari', 'mai': 'Maithili',
                'bh': 'Bhojpuri', 'awa': 'Awadhi', 'rom': 'Romany', 'snd': 'Sindhi',
                'bal': 'Baluchi', 'pnb': 'Western Punjabi', 'ks': 'Kashmiri', 'sd': 'Sindhi',
                'gom': 'Goan Konkani', 'brx': 'Bodo', 'sat': 'Santali', 'kha': 'Khasi',
                'mni': 'Manipuri', 'lus': 'Mizo', 'njz': 'Nyishi', 'sg': 'Sango',
                'ln': 'Lingala', 'kg': 'Kongo', 'luo': 'Luo', 'kam': 'Kamba',
                'mer': 'Meru', 'kik': 'Kikuyu', 'luy': 'Luhya', 'gaz': 'West Central Oromo',
                'tir': 'Tigre', 'orm': 'Oromo', 'som': 'Somali', 'amh': 'Amharic',
                'tig': 'Tigrinya', 'aar': 'Afar', 'ssw': 'Swati', 'nbl': 'Southern Ndebele',
                'nso': 'Northern Sotho', 'tso': 'Tsonga', 'ven': 'Venda', 'tsn': 'Tswana',
                'nya': 'Nyanja', 'bem': 'Bemba', 'lua': 'Luba-Katanga', 'kbp': 'Kabiyè',
                'dag': 'Dagbani', 'ewe': 'Ewe', 'fon': 'Fon', 'ibb': 'Ibibio',
                'ada': 'Adangme', 'gaa': 'Ga', 'sus': 'Susu', 'man': 'Mandingo',
                'dyu': 'Dyula', 'bam': 'Bambara', 'sen': 'Songhay', 'ful': 'Fulah',
                'wol': 'Wolof', 'srr': 'Serer', 'dga': 'Dagaare', 'mos': 'Mooré',
                'bci': 'Baoulé', 'men': 'Mende', 'tem': 'Timne', 'lim': 'Limburgish',
                'zea': 'Zeelandic', 'vls': 'West Flemish', 'frr': 'Northern Frisian',
                'gos': 'Gronings', 'nds': 'Low German', 'pfl': 'Palatinate German',
                'swg': 'Swabian German', 'bar': 'Bavarian', 'cim': 'Cimbrian',
                'gmw-cfr': 'Central Franconian', 'ksh': 'Kölsch', 'pdc': 'Pennsylvania German',
                'yid': 'Yiddish', 'lad': 'Ladino', 'jrb': 'Judeo-Arabic', 'jpr': 'Judeo-Persian',
                'mul': 'Multiple languages', 'und': 'Undetermined', 'zxx': 'No linguistic content'
            }
            
            # Add more language codes dynamically for 1000+ coverage
            additional_languages = {
                # African languages
                'ak': 'Akan', 'bm': 'Bambara', 'ee': 'Ewe', 'ff': 'Fulah', 'kl': 'Kalaallisut',
                'kr': 'Kanuri', 'lg': 'Ganda', 'ln': 'Lingala', 'mg': 'Malagasy', 'rn': 'Rundi',
                'sg': 'Sango', 'sn': 'Shona', 'st': 'Sotho', 'to': 'Tonga', 'ts': 'Tsonga',
                'tn': 'Tswana', 've': 'Venda', 'wo': 'Wolof', 'xh': 'Xhosa', 'yo': 'Yoruba',
                'zu': 'Zulu',
                
                # Asian languages
                'as': 'Assamese', 'bho': 'Bhojpuri', 'doi': 'Dogri', 'gom': 'Konkani',
                'kok': 'Konkani', 'mni': 'Manipuri', 'brx': 'Bodo', 'sat': 'Santali',
                'srx': 'Sirmauri', 'tdg': 'Western Tamang', 'taj': 'Eastern Tamang',
                'tsj': 'Tshangla', 'xnr': 'Kangri', 'hne': 'Chhattisgarhi', 'bgc': 'Haryanvi',
                'kfy': 'Kumaoni', 'bfy': 'Bagheli', 'bjj': 'Kanauji', 'gbm': 'Garhwali',
                'kfr': 'Kachchi', 'noe': 'Nimadi', 'sck': 'Sadri', 'swv': 'Shekhawati',
                'wtm': 'Mewati', 'dhd': 'Dhundari', 'mup': 'Malvi', 'wbr': 'Wagdi',
                'kfv': 'Kurmukar', 'kfb': 'Koli', 'kfg': 'Kudiya', 'xsr': 'Sherpa',
                'lif': 'Limbu', 'mjz': 'Majhi', 'bap': 'Bantawa', 'rjb': 'Rajbanshi',
                'kyv': 'Kayort', 'thl': 'Dangaura Tharu', 'tkt': 'Kathoriya Tharu',
                'kxp': 'Wadiyara Koli', 'gbl': 'Gamit', 'vas': 'Vasavi', 'kno': 'Kono',
                'kqs': 'Kissi', 'bkm': 'Kom', 'nmu': 'Namo', 'dts': 'Toro So Dogon',
                'kdl': 'Tsikimba', 'kdh': 'Tem', 'kdz': 'Kwaja', 'kdp': 'Kaningdon',
                'kdf': 'Mamusi', 'kde': 'Makonde', 'kdd': 'Yankunytjatjara',
                
                # European minority languages
                'sms': 'Skolt Sami', 'sma': 'Southern Sami', 'smn': 'Inari Sami',
                'smj': 'Lule Sami', 'se': 'Northern Sami', 'cv': 'Chuvash', 'kv': 'Komi',
                'myv': 'Erzya', 'mdf': 'Moksha', 'udm': 'Udmurt', 'koi': 'Komi-Permyak',
                'kpy': 'Koryak', 'ckt': 'Chukot', 'ess': 'Central Siberian Yupik',
                'ems': 'Alutiiq', 'esi': 'North Alaskan Inupiatun', 'esu': 'Central Yupik',
                
                # Middle Eastern languages
                'arc': 'Aramaic', 'syc': 'Classical Syriac', 'aii': 'Assyrian Neo-Aramaic',
                'cld': 'Chaldean Neo-Aramaic', 'tru': 'Turoyo', 'mid': 'Mandaic',
                'sam': 'Samaritan Aramaic', 'jpa': 'Jewish Palestinian Aramaic',
                
                # Pacific languages
                'haw': 'Hawaiian', 'rar': 'Rarotongan', 'tah': 'Tahitian', 'ton': 'Tongan',
                'smo': 'Samoan', 'fij': 'Fijian', 'hif': 'Fiji Hindi', 'gil': 'Gilbertese',
                'mri': 'Maori', 'niu': 'Niuean', 'pau': 'Palauan', 'pon': 'Pohnpeian',
                'chk': 'Chuukese', 'kos': 'Kosraean', 'yap': 'Yapese', 'uli': 'Ulithian',
                'wol': 'Woleaian', 'nkr': 'Nukuoro', 'kpg': 'Kapingamarangi',
                
                # Indigenous American languages
                'nav': 'Navajo', 'cre': 'Cree', 'oji': 'Ojibwe', 'chr': 'Cherokee',
                'cho': 'Choctaw', 'chy': 'Cheyenne', 'dak': 'Dakota', 'mus': 'Creek',
                'apa': 'Apache languages', 'ath': 'Athapaskan languages', 'alg': 'Algonquian languages',
                'iro': 'Iroquoian languages', 'myn': 'Mayan languages', 'azc': 'Uto-Aztecan languages',
                'oto': 'Otomian languages', 'cai': 'Central American Indian languages',
                'sai': 'South American Indian languages', 'nai': 'North American Indian languages',
                'crp': 'Creoles and pidgins', 'cpe': 'English-based creoles and pidgins',
                'cpf': 'French-based creoles and pidgins', 'cpp': 'Portuguese-based creoles and pidgins',
                'crp': 'Creoles and pidgins', 'crs': 'Seselwa Creole French',
                'jam': 'Jamaican Creole English', 'gul': 'Sea Island Creole English',
                'srn': 'Sranan Tongo', 'pcm': 'Nigerian Pidgin', 'wes': 'Cameroon Pidgin English',
                'tpi': 'Tok Pisin', 'bis': 'Bislama', 'pis': 'Pijin', 'ltz': 'Luxembourgish',
                'cos': 'Corsican', 'arg': 'Aragonese', 'cat': 'Catalan', 'glg': 'Galician',
                'roh': 'Romansh', 'srd': 'Sardinian', 'oci': 'Occitan', 'ast': 'Asturian',
                'scn': 'Sicilian', 'nap': 'Neapolitan', 'lmo': 'Lombard', 'eml': 'Emilian-Romagnol',
                'pms': 'Piedmontese', 'vec': 'Venetian', 'fur': 'Friulian', 'lad': 'Ladino',
                'frp': 'Franco-Provençal', 'wln': 'Walloon', 'gsw': 'Swiss German', 'bar': 'Bavarian',
                'ksh': 'Colognian', 'lim': 'Limburgish', 'zea': 'Zeelandic', 'vls': 'West Flemish',
                'fry': 'West Frisian', 'frr': 'North Frisian', 'gos': 'Gronings', 'nds': 'Low German',
                'pfl': 'Palatine German', 'swg': 'Swabian German', 'sxu': 'Upper Saxon German',
                'hrx': 'Hunsrik', 'pdt': 'Plautdietsch', 'yec': 'Yeniche', 'rmy': 'Vlax Romani',
                'rmn': 'Balkan Romani', 'rml': 'Baltic Romani', 'rmc': 'Carpathian Romani',
                'rmw': 'Welsh Romani', 'rme': 'Angloromani', 'rmo': 'Sinte Romani',
                'rmu': 'Tavringer Romani', 'rmf': 'Kalo Finnish Romani', 'rmg': 'Traveller Norwegian',
                'rmq': 'Caló', 'rtm': 'Rotuman', 'rth': 'Ratahan', 'rwr': 'Marwari',
                'rwk': 'Rwa', 'rug': 'Roviana', 'ruf': 'Luguru', 'rue': 'Rusyn',
                'rub': 'Gungu', 'rua': 'Ruund', 'rts': 'Yurats', 'rtc': 'Rungtu Chin',
                'rjs': 'Rajbanshi', 'rji': 'Raji', 'rjb': 'Rajbanshi', 'ria': 'Riang',
                'rgk': 'Rangkas', 'rwr': 'Marwari', 'saf': 'Safaliba', 'sah': 'Yakut',
                'sam': 'Samaritan Aramaic', 'san': 'Sanskrit', 'sas': 'Sasak',
                'sat': 'Santali', 'saz': 'Saurashtra', 'sba': 'Ngambay', 'sbe': 'Saliba',
                'sbl': 'Botolan Sambal', 'scs': 'North Slavey', 'sdc': 'Sassarese Sardinian',
                'sdh': 'Southern Kurdish', 'see': 'Seneca', 'sef': 'Cebaara Senufo',
                'seh': 'Sena', 'sei': 'Seri', 'ses': 'Koyraboro Senni Songhai',
                'sga': 'Old Irish', 'sgs': 'Samogitian', 'shi': 'Tachelhit', 'shk': 'Shilluk',
                'shn': 'Shan', 'shs': 'Shuswap', 'sia': 'Akkala Sami', 'sid': 'Sidamo',
                'sig': 'Paasaal', 'sil': 'Sisaala', 'sim': 'Mende', 'sjw': 'Shawnee',
                'skr': 'Saraiki', 'slr': 'Salar', 'sly': 'Selayar', 'sm': 'Samoan',
                'sml': 'Central Sama', 'smm': 'Musasa', 'smp': 'Samaritan', 'smq': 'Samo',
                'sms': 'Skolt Sami', 'snh': 'Shinabo', 'snp': 'Siane', 'snx': 'Sam',
                'sny': 'Saniyo-Hiyowe', 'soa': 'Thai Song', 'sok': 'Sokoro', 'soq': 'Kanasi',
                'sqt': 'Soqotri', 'sr': 'Serbian', 'srb': 'Sora', 'srm': 'Saramaccan',
                'srr': 'Serer', 'srx': 'Sirmauri', 'ssg': 'Seimat', 'ssy': 'Saho',
                'st': 'Southern Sotho', 'stb': 'Northern Subanen', 'ste': 'Liana-Seti',
                'stf': 'Seta', 'stg': 'Trieng', 'stk': 'Arammba', 'stm': 'Setaman',
                'stp': 'Southeastern Tepehuan', 'stw': 'Satawalese', 'sua': 'Sulka',
                'sue': 'Suena', 'sui': 'Suki', 'suk': 'Sukuma', 'sur': 'Mwaghavul',
                'sus': 'Susu', 'suv': 'Sulung', 'suy': 'Suyá', 'suz': 'Sunwar',
                'sv': 'Swedish', 'swb': 'Maore Comorian', 'swf': 'Sere', 'swg': 'Swabian',
                'swi': 'Sui', 'swj': 'Sira', 'swp': 'Suau', 'swq': 'Sharwa',
                'swr': 'Saweru', 'swt': 'Sawila', 'swu': 'Suwawa', 'swv': 'Shekhawati',
                'sww': 'Sowa', 'swx': 'Suruahá', 'swy': 'Sarua', 'sxb': 'Suba',
                'sxc': 'Sicanian', 'sxe': 'Sighu', 'sxg': 'Shixing', 'sxk': 'Southern Kalapuya',
                'sxm': 'Samre', 'sxn': 'Sangir', 'sxr': 'Saaroa', 'sxs': 'Sasaru',
                'sxu': 'Upper Saxon', 'sxw': 'Saxwe Gbe', 'sya': 'Siang', 'syb': 'Central Subanen',
                'syc': 'Classical Syriac', 'syi': 'Seki', 'syk': 'Sukur', 'syl': 'Sylheti',
                'sym': 'Maya Samo', 'syn': 'Senaya', 'syo': 'Suoy', 'sys': 'Sinyar',
                'syw': 'Kagate', 'sza': 'Semelai', 'szb': 'Ngalum', 'szc': 'Semaq Beri',
                'szd': 'Seru', 'sze': 'Seze', 'szg': 'Sengele', 'szl': 'Silesian',
                'szn': 'Sula', 'szp': 'Suabo', 'szs': 'Solomon Islands Sign Language',
                'szv': 'Isu', 'szw': 'Sawai', 'szy': 'Sakizaya', 'ta': 'Tamil',
                'tab': 'Tabassaran', 'taj': 'Eastern Tamang', 'tal': 'Tal',
                'tan': 'Tangale', 'taq': 'Tamasheq', 'tbc': 'Takia', 'tbd': 'Kaki Ae',
                'tbf': 'Mandara', 'tbg': 'North Tairora', 'tbh': 'Thurawal',
                'tbi': 'Gaam', 'tbj': 'Tiang', 'tbk': 'Calamian Tagbanwa',
                'tbl': 'Tboli', 'tbm': 'Tagbu', 'tbn': 'Barro Negro Tunebo',
                'tbo': 'Tawala', 'tbp': 'Taworta', 'tbq': 'Tibeto-Burman languages',
                'tbr': 'Tumtum', 'tbs': 'Tanguat', 'tbt': 'Tembo', 'tbu': 'Tubar',
                'tbv': 'Tobo', 'tbw': 'Tagbanwa', 'tbx': 'Kapin', 'tby': 'Tabaru',
                'tbz': 'Ditammari', 'tca': 'Ticuna', 'tcb': 'Tanacross', 'tcc': 'Datooga',
                'tcd': 'Tafi', 'tce': 'Southern Tutchone', 'tcf': 'Malinaltepec Me'phaa',
                'tcg': 'Tamagario', 'tch': 'Turks And Caicos Creole English',
                'tci': 'Wára', 'tck': 'Tchitchege', 'tcl': 'Taman', 'tcm': 'Tanahmerah',
                'tcn': 'Tichurong', 'tco': 'Taungyo', 'tcp': 'Tawr Chin', 'tcq': 'Kaiy',
                'tcs': 'Torres Strait Creole', 'tct': 'T'en', 'tcu': 'Southeastern Tarahumara',
                'tcw': 'Tecpatlán Totonac', 'tcx': 'Toda', 'tcy': 'Tulu', 'tcz': 'Thado Chin',
                'tda': 'Tagdal', 'tdb': 'Panchpargania', 'tdc': 'Emberá-Tadó',
                'tdd': 'Tai Nüa', 'tde': 'Tiranige Diga Dogon', 'tdf': 'Talieng',
                'tdg': 'Western Tamang', 'tdh': 'Thulung', 'tdi': 'Tomadino',
                'tdj': 'Tajio', 'tdk': 'Tambas', 'tdl': 'Sur', 'tdn': 'Tondano',
                'tdo': 'Toma', 'tdq': 'Tita', 'tdr': 'Todrah', 'tds': 'Doutai',
                'tdt': 'Tetun Dili', 'tdu': 'Tempasuk Dusun', 'tdv': 'Toro',
                'tdx': 'Tandroy-Mahafaly Malagasy', 'tdy': 'Tadyawan', 'te': 'Telugu',
                'tea': 'Temiar', 'teb': 'Tetete', 'tec': 'Terik', 'ted': 'Tepo Krumen',
                'tee': 'Huehuetla Tepehua', 'tef': 'Teressa', 'teg': 'Teke-Tege',
                'teh': 'Tehuelche', 'tei': 'Torricelli', 'tek': 'Ibali Teke',
                'tem': 'Timne', 'ten': 'Tama', 'teo': 'Teso', 'tep': 'Tepecano',
                'teq': 'Temein', 'ter': 'Tereno', 'tes': 'Tengger', 'tet': 'Tetum',
                'teu': 'Soo', 'tev': 'Teor', 'tew': 'Tewa', 'tex': 'Tennet',
                'tey': 'Tulishi', 'tfi': 'Tofin Gbe', 'tfn': 'Tanaina', 'tfo': 'Tefaro',
                'tfr': 'Teribe', 'tft': 'Ternate', 'tg': 'Tajik', 'tga': 'Sagalla',
                'tgb': 'Tobilung', 'tgc': 'Tigak', 'tgd': 'Ciwogai', 'tge': 'Eastern Gorkha Tamang',
                'tgf': 'Chalikha', 'tgg': 'Tangga', 'tgh': 'Tobagonian Creole English',
                'tgi': 'Lawunuia', 'tgj': 'Tagin', 'tgk': 'Tajik', 'tgl': 'Tagalog',
                'tgn': 'Tandaganon', 'tgo': 'Sudest', 'tgp': 'Tangoa', 'tgq': 'Tring',
                'tgr': 'Tareng', 'tgs': 'Nume', 'tgt': 'Central Tagbanwa', 'tgu': 'Tanggu',
                'tgv': 'Tingui-Boto', 'tgw': 'Tagwana Senoufo', 'tgx': 'Tagish',
                'tgy': 'Togoyo', 'tgz': 'Tagalaka', 'th': 'Thai', 'thd': 'Thayore',
                'the': 'Chitwania Tharu', 'thf': 'Thangmi', 'thh': 'Northern Tarahumara',
                'thi': 'Tai Long', 'thk': 'Tharaka', 'thl': 'Dangaura Tharu',
                'thm': 'Aheu', 'thn': 'Thachanadan', 'thp': 'Thompson', 'thq': 'Kochila Tharu',
                'thr': 'Rana Tharu', 'ths': 'Thakali', 'tht': 'Tahltan', 'thu': 'Thuri',
                'thv': 'Tahaggart Tamahaq', 'thw': 'Thudam', 'thy': 'Tha', 'thz': 'Tayart Tamajeq',
                'ti': 'Tigrinya', 'tia': 'Tidikelt Tamazight', 'tic': 'Tira', 'tid': 'Tidong',
                'tif': 'Tifal', 'tig': 'Tigre', 'tih': 'Timugon Murut', 'tii': 'Tiene',
                'tij': 'Tilung', 'tik': 'Tikar', 'til': 'Tillamook', 'tim': 'Timbe',
                'tin': 'Tindi', 'tio': 'Teop', 'tip': 'Trimuris', 'tiq': 'Tiéfo',
                'tis': 'Masadiit Itneg', 'tit': 'Tinigua', 'tiu': 'Adasen', 'tiv': 'Tiv',
                'tiw': 'Tiwi', 'tix': 'Southern Tiwa', 'tiy': 'Tiruray', 'tiz': 'Tai Hongjin',
                'tja': 'Tajuasohn', 'tjg': 'Tunjung', 'tji': 'Northern Tujia', 'tjl': 'Tai Laing',
                'tjm': 'Timucua', 'tjn': 'Tonjon', 'tjo': 'Temacine Tamazight', 'tjp': 'Tjupany',
                'tjs': 'Southern Tujia', 'tju': 'Tjurruru', 'tjw': 'Djabwurrung',
                'tk': 'Turkmen', 'tka': 'Truká', 'tkb': 'Buksa', 'tkd': 'Tukudede',
                'tke': 'Takwane', 'tkf': 'Tukumanféd', 'tkg': 'Tesaka Malagasy',
                'tkl': 'Tokelau', 'tkm': 'Takelma', 'tkn': 'Toku-No-Shima', 'tkp': 'Tikopia',
                'tkq': 'Tee', 'tkr': 'Tsakhur', 'tks': 'Takestani', 'tkt': 'Kathoriya Tharu',
                'tku': 'Upper Necaxa Totonac', 'tkv': 'Mur Pano', 'tkw': 'Teanu',
                'tkx': 'Tangko', 'tkz': 'Takua', 'tl': 'Tagalog', 'tla': 'Southwestern Tepehuan',
                'tlb': 'Tobelo', 'tlc': 'Yecuatla Totonac', 'tld': 'Talaud', 'tlf': 'Telefol',
                'tlg': 'Tofanma', 'tlh': 'Klingon', 'tli': 'Tlingit', 'tlj': 'Talinga-Bwisi',
                'tlk': 'Taloki', 'tll': 'Tetela', 'tlm': 'Tolomako', 'tln': 'Talondo',
                'tlo': 'Talodi', 'tlp': 'Filomena Mata-Coahuitlán Totonac',
                'tlq': 'Tai Loi', 'tlr': 'Talise', 'tls': 'Tambotalo', 'tlt': 'Sou Nama',
                'tlu': 'Tulehu', 'tlv': 'Taliabu', 'tlx': 'Khehek', 'tly': 'Talysh',
                'tma': 'Tama', 'tmb': 'Katbol', 'tmc': 'Tumak', 'tmd': 'Haruai',
                'tme': 'Tremembé', 'tmf': 'Toba-Maskoy', 'tmg': 'Ternateño',
                'tmh': 'Tamashek', 'tmi': 'Tutuba', 'tmj': 'Samarokena', 'tmk': 'Northwestern Tamang',
                'tml': 'Tamnim Citak', 'tmm': 'Tai Thanh', 'tmn': 'Taman', 'tmo': 'Temoq',
                'tmp': 'Tai Mène', 'tmq': 'Tumleo', 'tmr': 'Jewish Babylonian Aramaic',
                'tms': 'Tima', 'tmt': 'Tasmate', 'tmu': 'Iau', 'tmv': 'Tembo',
                'tmw': 'Temuan', 'tmy': 'Tami', 'tmz': 'Tamanaku', 'tn': 'Tswana',
                'tna': 'Tacana', 'tnb': 'Western Tunebo', 'tnc': 'Tanimuca-Retuarã',
                'tnd': 'Angosturas Tunebo', 'tne': 'Tinoc Kallahan', 'tnf': 'Tangshewi',
                'tng': 'Tobanga', 'tnh': 'Maiani', 'tni': 'Tandia', 'tnk': 'Kwamera',
                'tnl': 'Lenakel', 'tnm': 'Tabla', 'tnn': 'North Tanna', 'tno': 'Toromono',
                'tnp': 'Whitesands', 'tnq': 'Taino', 'tnr': 'Ménik', 'tns': 'Tenis',
                'tnt': 'Tontemboan', 'tnu': 'Tay Khang', 'tnv': 'Tangchangya',
                'tnw': 'Tonsawang', 'tnx': 'Tanema', 'tny': 'Tongwe', 'tnz': 'Ten',
                'to': 'Tongan', 'tob': 'Toba', 'toc': 'Coyutla Totonac', 'tod': 'Toma',
               
