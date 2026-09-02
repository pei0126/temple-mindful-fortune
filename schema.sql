-- ==============================================================================
-- SQLite 資料庫結構定義 (線上宮廟智慧解籤系統 - 260 首傳統靈籤完整版)
-- 包含：六十甲子籤 (60首)、關聖帝君一百籤 (100首)、觀音靈籤一百首 (100首)
-- ==============================================================================

-- 1. 籤詩基本資料表 (lots)
CREATE TABLE IF NOT EXISTS lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_type TEXT NOT NULL,                       -- 籤詩系統類別 (60_jiazi / guandi_100 / guanyin_100)
    lot_type_name TEXT NOT NULL,                  -- 籤詩系統名稱 (六十甲子籤 / 關聖帝君一百籤 / 觀音靈籤一百首)
    lot_number INTEGER NOT NULL,                  -- 籤號 (1 ~ 60 或 1 ~ 100)
    lot_name TEXT NOT NULL,                       -- 籤名 (例如：第一籤 甲子、第一籤 甲甲、第一籤)
    grade TEXT NOT NULL,                          -- 吉凶等級 (大吉、上上、上吉、中吉、中平、下下等)
    content TEXT NOT NULL,                        -- 籤詩原文 (四句七言/五言詩)
    story TEXT NOT NULL,                          -- 典故由來與歷史象徵
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(lot_type, lot_number)
);

CREATE INDEX IF NOT EXISTS idx_lots_type_number ON lots(lot_type, lot_number);

-- 2. 抽籤與 AI 解析紀錄表 (user_draws)
CREATE TABLE IF NOT EXISTS user_draws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER,
    lot_type TEXT DEFAULT '60_jiazi',
    lot_number INTEGER NOT NULL,
    user_question TEXT NOT NULL,
    ai_analysis TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_user_draws_created_at ON user_draws(created_at DESC);

-- ==============================================================================
-- 3. 籤詩資料注入 (260 首完整種子資料)
-- ==============================================================================
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 1, '第一籤 甲子', '大吉', '日出便見風雲散，
光明清淨照世間。
一向前途通大道，
萬事清吉保平安。', '包公請雷神。象徵黑夜將過、天理昭彰，烏雲終會散去迎來曙光。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 2, '第二籤 乙丑', '中吉', '盈虛消息總天時，
自此君當百事宜。
若問前程歸縮地，
更須方寸好修為。', '姜太公釣魚。象徵凡事皆有其自然興衰週期，當下宜沉住氣修身養性，待時機成熟自然水到渠成。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 3, '第三籤 丙寅', '中平', '財中漸漸見分明，
花開花謝結子成。
寬心且看月中桂，
郎君即便見太平。', '孟郊五十登第。象徵長期的耕耘即將看見輪廓，需有耐心等待開花結果，切勿急躁冒進。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 4, '第四籤 丁卯', '中吉', '風恬浪靜可行舟，
恰是中秋月一輪。
凡事不須多憂慮，
福祿自有慶家門。', '趙子龍救阿斗。象徵風平浪靜、局勢漸穩，只要依循正直本心行動，憂慮自能化解。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 5, '第五籤 戊辰', '下平', '只恐前途明有變，
各須撥雲弄巧來。
若得貴人相引處，
自然門戶可生財。', '蘇秦不第。象徵目前局勢存在變數與不確定性，切忌單打獨鬥，宜尋求良師益友或外部專業協助。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 6, '第六籤 己巳', '大吉', '風雲致雨落天涯，
錦繡成針力可嘉。
幸有神仙來引路，
滿天桃李自開花。', '韓文公過秦嶺。象徵歷經一番寒徹骨後終得轉機，腳踏實地的努力將在關鍵時刻得到指引與回報。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 7, '第七籤 庚午', '中平', '雲遮月色正朦朧，
且向江頭聽晚鐘。
看盡人間興廢事，
古今得失問英雄。', '莊子試妻。象徵處於迷茫與觀望期，當下不宜做出重大冒進抉擇，宜退一步冷靜觀察全局。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 8, '第八籤 辛未', '上吉', '禾稻看看結成完，
此事必定兩相全。
回到家中寬心坐，
妻兒鼓舞樂團圓。', '李密投唐。象徵付出已累積至收穫期，目標漸趨成熟，保持安心與正向心態即可迎接圓滿成果。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 9, '第九籤 壬申', '中吉', '看君來問心中事，
積善之家慶有餘。
運亨財子雙雙至，
指日喜氣溢門楣。', '趙匡胤登基。象徵過往的善意與誠信將在當下轉化為實質助力，順應良善初衷行動必有佳音。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 10, '第十籤 癸酉', '中平', '花開結子一半枯，
可惜今年撫牧疏。
漸漸祥光來照耀，
自然家室得安居。', '岳飛抗金。象徵過往或有疏忽與不足之處，但只要正視問題、重新調整方向，轉機隨之而來。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 11, '第十一籤 甲戌', '大吉', '靈雞漸漸見分明，
凡事且看子丑寅。
雲開月出照天下，
郎君即便見太平。', '韓信拜將。象徵熬過蟄伏時期，時機將於關鍵時刻成熟，展現長才的大好舞台即將登場。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 12, '第十二籤 乙亥', '中吉', '長江風浪漸漸靜，
于今得進可安寧。
必有貴人相扶助，
凶事脫出見太平。', '蘇東坡遊赤壁。象徵經歷風浪之後情勢逐漸平息，將有貴人或新視角協助化險為夷。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 13, '第十三籤 丙子', '中平', '命中正逢羅孛關，
用盡心機總未休。
作福修因求佛庇，
神明指點莫疑猜。', '呂蒙正中狀元。象徵正面臨考驗關卡，單靠心計不如沉潛修為、修心養德以待翻身之機。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 14, '第十四籤 丁丑', '中吉', '財中漸漸見分明，
花開花謝結子成。
寬心且看月中桂，
郎君即便見太平。', '桃園三結義。象徵同心協力與階段性進展，只要目標一致，努力終將在特定時節結出成果。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 15, '第十五籤 戊寅', '中平', '八仙過海各顯通，
凡事莫隨大水流。
得寬懷處且寬懷，
萬事逢春漸見開。', '張旭醉墨。象徵每個人各有專長與節奏，莫盲目跟從潮流，保持心胸豁達自能柳暗花明。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 16, '第十六籤 己卯', '上吉', '耕耘只在手頭功，
積穀防饑要用工。
若得秋收成大獲，
倉箱處處有餘充。', '神農嘗百草。象徵踏實耕耘的累積效益，著眼於日常的基礎功夫，秋後自有一番豐盛收穫。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 17, '第十七籤 庚辰', '中平', '富貴由天莫強求，
門庭清吉免招憂。
勸君守分隨緣過，
必定前程得自由。', '莊子鼓盆。象徵順應自然、不執著於功名浮華，守住本心生活反而能得到真正的解脫與自在。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 18, '第十八籤 辛巳', '上吉', '君問中間此言因，
看看祿馬拱前程。
若得貴人相引處，
自然門戶可生金。', '百里奚相秦。象徵懷才終會遇知音，在良師或益友的提攜下，事業與前途將迎來開闊格局。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 19, '第十九籤 壬午', '中吉', '平生富貴成祿位，
今日榮華得意時。
若得貴人相助力，
前程萬里任西東。', '紅拂女夜奔。象徵果斷與勇氣帶來的命運轉折，把握得力機緣勇敢啟程，前途海闊天空。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 20, '第二十籤 癸未', '下平', '前途功名未得意，
只恐命內有交加。
兩家門戶各相爭，
惹得公事到官衙。', '蘇武牧羊。象徵當前受困於紛爭與對立，切勿意氣用事捲入糾紛，需秉持堅定節操熬過寒冬。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 21, '第二十一籤 甲申', '大吉', '十方佛法有靈通，
大難禍患不相同。
紅日當空常照耀，
還有貴人到身邊。', '孫悟空大鬧天宮。象徵處境雖有波折與挑戰，但有強大智慧與外力相助，終能化險為夷光明朗照。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 22, '第二十二籤 乙酉', '下下', '舊恨重重未改為，
家中禍患兩相催。
押來押去未分明，
何日得見光輝照。', '李世民遊地府。象徵內心積壓過多舊有矛盾與負面執念，需徹底反省釋懷方能走出幽谷。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 23, '第二十三籤 丙戌', '中平', '欲去長江浪渺茫，
前途未遂運未通。
如今且守波濤靜，
待得春來草自生。', '周瑜赤壁之戰。象徵前路局勢迷濛風浪大，當下宜蓄積實力靜觀其變，不宜強行冒險行舟。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 24, '第二十四籤 丁亥', '大吉', '月出光輝四海明，
前途祿位正亨通。
勸君把定心頭志，
萬事清吉保太平。', '司馬懿破八陣圖。象徵守得雲開見月明，堅定內心理想與定力，自能迎來全面開展之局。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 25, '第二十五籤 戊子', '中吉', '總是前途莫心疑，
勸君且退免災危。
莫嫌步步多艱難，
會有青雲得路時。', '狄青取珍珠旗。象徵以退為進的智慧，路途雖有艱難險阻，只要腳步堅定終將登上青雲之路。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 26, '第二十六籤 己丑', '大吉', '選出牡丹第一枝，
勸君折取莫遲疑。
世間富貴與榮華，
莫向他人求富兒。', '薛仁貴救駕。象徵絕佳機會就在眼前，當機立斷展現自我，不假外求自得豐盛成果。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 27, '第二十七籤 庚寅', '上吉', '君爾何須問前程，
須知命內合亨通。
若問功名謀望事，
寬心且看月中春。', '包公治陳州。象徵光明磊落自有福報，不必為未來過度焦慮，順應天時自然水到渠成。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 28, '第二十八籤 辛卯', '中吉', '東西南北不禁行，
前途此去得通亨。
若問功名並財利，
如今且得貴人迎。', '司馬相如題橋。象徵四方通達無所障礙，出門行事皆得助力，是積極開拓的良機。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 29, '第二十九籤 壬辰', '中平', '枯木可惜未逢春，
如今且在暗中藏。
寬心待得陽春至，
萬物萌芽發自香。', '姜子牙賣麵。象徵處於能量蓄積的蟄伏期，無須悲觀失意，養精蓄銳靜待春風吹拂。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 30, '第三十籤 癸巳', '中吉', '漸漸濃雲光少明，
看看歲暮進前程。
莫嫌步步多艱阻，
終見清光照世間。', '薛仁貴回家。象徵倒吃甘蔗漸入佳境，即便歲末年節前有波折阻礙，堅持到底終見光明。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 31, '第三十一籤 甲午', '上吉', '綠柳蒼蒼正當時，
任君步步進前程。
莫將心事掛疑慮，
自有貴人相扶持。', '孟姜女尋夫。象徵機遇成熟綠意盎然，放下心中的懷疑與裹足不前，大膽邁步自得助力。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 32, '第三十二籤 乙未', '中平', '前途功名未得時，
勸君且退莫遲疑。
如今且守波濤靜，
會有青雲得路時。', '龍虎相鬥。象徵時運未濟時不可硬碰硬，適時退讓避開鋒芒，方能在未來找到真正的出路。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 33, '第三十三籤 丙申', '中吉', '欲問前途何日通，
寬心且待遇春風。
如今且守波濤靜，
待得良時吉慶重。', '鮑叔牙薦管仲。象徵寬容厚道必有佳報，靜心等待和風送暖，吉慶喜事將接踵而至。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 34, '第三十四籤 丁酉', '大吉', '紅日當空正照耀，
凡事亨通得自由。
若問功名並財利，
貴人相引步青雲。', '曹操刺董卓。象徵局勢如日中天光明正大，正是展現抱負、追求卓越的最佳時刻。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 35, '第三十五籤 戊戌', '中平', '命內功名各不同，
勸君莫怨運難通。
如今且守波濤靜，
待得春來草自豐。', '管鮑分金。象徵接納個別差異與節奏，不怨天尤人，專注於自我滋養等待春意萌發。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 36, '第三十六籤 己亥', '大吉', '福如東海壽南山，
萬里鵬程在此間。
若問功名並財利，
榮華富貴得平安。', '薛仁貴征東。象徵格局宏大宏圖大展，福澤深厚，行事皆能平安順利達成目標。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 37, '第三十七籤 庚子', '中吉', '運逢得意身顯榮，
貴人指引步青雲。
如今且守波濤靜，
會有金榜掛姓名。', '楚霸王自刎。象徵得意之時更需保持謙遜與警醒，穩健行事方能長久保有榮耀。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 38, '第三十八籤 辛丑', '中平', '漸漸祥光來照耀，
凡事亨通得自由。
勸君把定心頭志，
莫向他人問底由。', '劉備借荊州。象徵曙光漸現，最重要的是相信自己的判斷與定力，勿被旁人流言所左右。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 39, '第三十九籤 壬寅', '中平', '意中若問神仙術，
勸君且退莫遲疑。
如今且守波濤靜，
待得良時吉慶兒。', '張良尋師。象徵勿迷信走捷徑或神異之說，腳踏實地修習專業本領，自能迎來良時。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 40, '第四十籤 癸卯', '中平', '門庭清吉免招憂，
勸君守分隨緣過。
命中註定無偏差，
會有榮華富貴誇。', '宋江聚義。象徵守護當下平穩狀態，隨順因緣不強求，一切皆在最好的安排之中。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 41, '第四十一籤 甲辰', '中吉', '枯木逢春再發芽，
如今且在暗中藏。
寬心待得良時至，
自然門戶得光華。', '伍子胥過昭關。象徵歷經考驗重生復甦，沉潛蓄力後即將煥發全新生機與光彩。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 42, '第四十二籤 乙巳', '上吉', '禾稻結成富貴春，
如今且在暗中藏。
勸君把定心頭志，
會有青雲得路時。', '關雲長斬顏良。象徵實力早已到位，只要把握時機展現堅定意志，必能一戰成名。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 43, '第四十三籤 丙午', '中平', '欲求富貴莫心疑，
如今且守波濤靜。
待得春來草木發，
自然門戶得安寧。', '薛平貴回窯。象徵堅守信念歷久彌堅，耐得住寂寞與等待，家業前程自能安泰。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 44, '第四十四籤 丁未', '上吉', '綠柳蒼蒼正當時，
任君步步進前程。
莫將心事掛疑慮，
會有貴人相扶持。', '蕭何追韓信。象徵惜才愛才得到關鍵知遇，放下顧慮邁開大步，前途璀璨可期。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 45, '第四十五籤 戊申', '中平', '富貴由天莫強求，
門庭清吉免招憂。
勸君守分隨緣過，
必定前程得自由。', '楊文廣陷柳州。象徵處於考驗中宜保持冷靜沉著，不盲動強求，平安即是最大福份。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 46, '第四十六籤 己酉', '中吉', '漸漸濃雲光少明，
看看歲暮進前程。
莫嫌步步多艱阻，
終見清光照世間。', '狄青平南。象徵排除萬難逐步突破，雖然過程辛苦，但勝利的曙光已在眼前。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 47, '第四十七籤 庚戌', '大吉', '雲開月出正分明，
不須進退問前程。
婚姻月老扶持吉，
貴人指引步青雲。', '高祖起義。象徵風雲開朗前路無礙，各方貴人齊聚相挺，成就大事指日可待。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 48, '第四十八籤 辛亥', '中吉', '命內功名各不同，
勸君莫怨運難通。
如今且守波濤靜，
待得春來草自豐。', '班超投筆從戎。象徵找對屬於自己的天賦戰場，轉念變通即可開闢一番非凡事業。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 49, '第四十九籤 壬子', '中平', '枯木逢春再發芽，
如今且在暗中藏。
寬心待得良時至，
自然門戶得光華。', '陸遜營燒連營。象徵沉著布局等待對手露出破綻，時機成熟時自能一舉扭轉局勢。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 50, '第五十籤 癸丑', '大吉', '意中若問神仙術，
勸君且退莫遲疑。
如今且守波濤靜，
待得良時吉慶兒。', '郭子儀拜壽。象徵福祿雙全滿堂吉慶，歷經滄桑後收穫最豐厚圓滿的人生答卷。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 51, '第五十一籤 甲寅', '上吉', '東西南北不禁行，
前途此去得通亨。
若問功名並財利，
如今且得貴人迎。', '趙玄壇得道。象徵財源廣進四通八達，行事如順水行舟，得各界貴人鼎力相助。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 52, '第五十二籤 乙卯', '中平', '門庭清吉免招憂，
勸君守分隨緣過。
命中註定無偏差，
會有榮華富貴誇。', '黃巢起義。象徵當下宜沉住氣守本份，切忌衝動盲動破壞平衡，靜待更佳轉機。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 53, '第五十三籤 丙辰', '上吉', '八仙過海各顯通，
凡事莫隨大水流。
得寬懷處且寬懷，
萬事逢春漸見開。', '蘇秦封相。象徵熬過低谷終獲六國相印，發揮自身獨特優勢，榮耀歸來。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 54, '第五十四籤 丁巳', '上吉', '耕耘只在手頭功，
積穀防饑要用工。
若得秋收成大獲，
倉箱處處有餘充。', '呂洞賓度何仙姑。象徵點滴修行與付出終成正果，持之以恆必能得道豐收。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 55, '第五十五籤 戊午', '大吉', '禾稻看看結成完，
此事必定兩相全。
回到家中寬心坐，
妻兒鼓舞樂團圓。', '姜太公得道。象徵八十遇文王，大器晚成兩相全美，欣享合家安樂福報。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 56, '第五十六籤 己未', '大吉', '看君來問心中事，
積善之家慶有餘。
運亨財子雙雙至，
指日喜氣溢門楣。', '范蠡遊五湖。象徵功成身退逍遙自在，智勇雙全商界稱雄，迎來最豐盛人生。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 57, '第五十七籤 庚申', '中吉', '花開結子一半枯，
可惜今年撫牧疏。
漸漸祥光來照耀，
自然家室得安居。', '董永皇天不負。象徵孝行感動天地，困頓中終獲仙緣相助，家道重現光明。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 58, '第五十八籤 辛酉', '上吉', '靈雞漸漸見分明，
凡事且看子丑寅。
雲開月出照天下，
郎君即便見太平。', '蘇武歸漢。象徵十九年苦節終得昭雪，榮歸故里揚名立萬，苦盡甘來。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 59, '第五十九籤 壬戌', '大吉', '姥姥持齋去拜佛，
只求兒孫受封封。
佛爺慈悲施恩澤，
合家老幼得安寧。', '漢高祖得天下。象徵大局底定四海昇平，長輩積德庇蔭子孫，家業長久安寧。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('60_jiazi', '六十甲子籤', 60, '第六十籤 癸亥', '中平', '命中正逢羅孛關，
用盡心機總未休。
作福修因求佛庇，
神明指點莫疑猜。', '楊令公撞李陵碑。象徵面對最後險關需以忠烈坦蕩之心相對，放下執念，圓滿收尾。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 1, '第一籤 甲甲', '大吉', '巍巍獨步向雲間，
玉殿千官第一班。
富貴榮華天付汝，
福如東海壽如山。', '漢高祖入關。象徵獨占鰲頭、德位相配，長期的積累與格局將迎來至高榮耀與深厚福澤。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 2, '第二籤 甲乙', '上吉', '盈虛消息總天時，
自此君當百事宜。
若問前程歸縮地，
更須方寸好修為。', '張子房遊赤松。象徵懂得天道循環興衰之理，功成身退明哲保身，心存良善方能萬事亨通。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 3, '第三籤 甲丙', '中吉', '衣食自然豐裕足，
莫聽旁人說是非。
好把身心全放下，
神明自必暗相隨。', '賈誼遇漢文帝。象徵自身條件與資源充足，切勿受外界雜音動搖，守住內在安定自得庇佑。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 4, '第四籤 甲丁', '下下', '去年百事頗相宜，
若較今年時運衰。
好把身心且收斂，
莫教惹起禍殃來。', '小吏伏案。象徵時局轉換、風頭已變，當下切忌沿用過往擴張心態，宜全面收斂防守以保平安。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 5, '第五籤 甲戊', '中平', '子有三般不自由，
門庭蕭索冷如秋。
若逢牛鼠交承日，
萬事回春不用憂。', '呂蒙正守困。象徵當前處境身不由己、備受約束，但只要耐住性子等待時節轉折，春暖花開終將到來。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 6, '第六籤 甲己', '中吉', '相逢話墮為投機，
一片冰心世少知。
若得知音相引領，
何愁白日不光輝。', '司馬相如題橋。象徵懷才抱德雖暫時孤寂，但一旦遇得相知貴人提攜引薦，必能大放異彩。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 7, '第七籤 甲庚', '大吉', '仙風道骨本天生，
得遇真仙便作仙。
莫向迷途深處走，
回頭便是大羅天。', '呂洞賓遇鍾離權。象徵根基深厚具備高維覺悟，只要即時察覺盲點回頭轉向，即入全新寬廣格局。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 8, '第八籤 甲辛', '上吉', '年來耕稼苦無收，
今歲田疇大有秋。
況遇太平無事日，
士農工商業優遊。', '大舜耕歷山。象徵過往的艱辛播種即將在今年迎來大豐收，順應安定環境各展所長自由優遊。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 9, '第九籤 甲壬', '中吉', '望渠消息向長安，
常把菱花仔細看。
見說新來稱意汝，
眼前富貴賞芳蘭。', '宋仁宗認母。象徵期盼已久的好消息即將傳來，整理好自身儀態與心態，欣然迎接稱心如意之境。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 10, '第十籤 甲癸', '下下', '病患時時命蹇衰，
何須禱告向神祇。
但能積德行方便，
自保身安免是非。', '冉伯牛染病。象徵目前身心能量低落或處境困頓，外求無益，唯有從根本內省、修身積德方能轉危為安。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 11, '第十一籤 乙甲', '大吉', '今年好事番先歲，
況遇新春月正圓。
百事欣欣皆稱意，
更添福祿在門前。', '韓信配三齊王。象徵運勢全面翻新超越以往，正值天時地利人和之良機，凡事皆可放手施展。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 12, '第十二籤 乙乙', '中平', '營為期望在春前，
誰料秋來又不然。
直待水雲相映處，
迢迢前路便通連。', '蘇武牧羊。象徵短期計畫或有延宕落差，勿因此氣餒，待關鍵契機出現後，通達之道自然顯現。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 13, '第十三籤 乙丙', '中吉', '君是山中萬戶侯，
信知騎馬勝騎牛。
今朝馬上看雲髻，
直上青雲第一樓。', '姜公遇文王。象徵自具非凡器量與潛力，應勇敢追求更高遠目標，果斷乘勢而上登上巔峰。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 14, '第十四籤 乙丁', '下下', '一見佳人便喜歡，
誰知暗裡有波瀾。
莫教錯認同心結，
自惹閑愁淚不乾。', '郭華戀王月英。象徵切忌被表面美好或一時衝動所迷惑，背後藏有未見之風險，宜保持冷靜客觀。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 15, '第十五籤 乙戊', '中平', '兩家門戶各相當，
相見何須說短長。
好把身心全放下，
免教惹得是非纏。', '張良遇黃石公。象徵雙方實力旗鼓相當，無須爭強好勝逞口舌之快，放下我執才能免除是非糾葛。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 16, '第十六籤 乙己', '上吉', '秉燭夜行步步疑，
投明卻見滿天星。
如今且得通亨路，
莫向旁人問是非。', '王昭君和番。象徵走出摸黑疑慮的階段，晨光即現星光璀璨，堅定依循自己的道路邁進。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 17, '第十七籤 乙庚', '下下', '田園價貫好商量，
事到公庭各有傷。
早把身心全放下，
免教惹得是非長。', '石崇被難。象徵利益糾葛極易引發兩敗俱傷之禍，宜退讓協商尋求和解，切莫興訟爭執。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 18, '第十八籤 乙辛', '中吉', '知君身入富豪家，
富貴榮華自可誇。
若得貴人相引領，
自然門戶發光華。', '孟嘗君招賢。象徵身處有利平台與環境，只要虛心納諫並獲貴人指點，必能創造更大成就。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 19, '第十九籤 乙壬', '上吉', '嗟子從來未得時，
今年星運頗相宜。
營求動作都如意，
和合家庭喜氣盈。', '范蠡歸湖。象徵轉運之期已至，過去的壓抑將化為順遂能量，行事動作皆稱心家庭和樂。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 20, '第二十籤 乙癸', '下下', '嚴顏未肯降張飛，
義氣干雲世所稀。
莫向迷途爭勝負，
退身一步免危微。', '嚴顏不降。象徵骨氣可嘉但形勢比人強，硬碰硬恐致無謂折損，退讓一步海闊天空。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 21, '第二十一籤 丙甲', '大吉', '意中若問神仙術，
勸君且退莫心疑。
若得良時並吉日，
自然門戶慶雙全。', '孫龐鬥智。象徵大道至簡無須外求巧詐，把握天時良機踏實布局，自得名利雙全之福。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 22, '第二十二籤 丙乙', '上吉', '年來耕稼苦無收，
今歲田疇大有秋。
士農工商皆得意，
欣欣向榮樂優遊。', '李密投唐。象徵經歷困頓後轉投明主或找到正確戰場，萬事皆順迎來欣欣向榮之勢。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 23, '第二十三籤 丙丙', '中平', '花開花謝在春風，
貴賤榮華各自同。
莫向旁人爭長短，
隨緣守分免災凶。', '吳王愛西施。象徵榮辱興衰自有定數，勿盲目攀比競爭，守分隨緣方能保平安。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 24, '第二十四籤 丙丁', '下下', '一春萬事苦憂煎，
夏裡營求亦未全。
秋至冬來多阻礙，
不如且退保身全。', '楊令公陷李陵碑。象徵整年局勢阻力重重、動輒得咎，當下以保全實力、休養生息為最高原則。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 25, '第二十五籤 丙戊', '中平', '困居幽谷聽啼禽，
欲向青雲未得伸。
若逢鼠牛相會日，
自然脫出見精神。', '趙子龍救幼主。象徵暫處困局未能展翅，耐心守候至特定契機（如年末或交接時節），必能突圍重振雄風。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 26, '第二十六籤 丙己', '上吉', '年來作事頗稱心，
財寶豐盈勝似金。
若問前程謀望事，
自然吉慶喜相尋。', '邵堯夫祝香。象徵心存天理吉星高照，謀望所成皆如意，前程光明喜事連連。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 27, '第二十七籤 丙庚', '中平', '世間萬事總由天，
何必營求苦掛牽。
隨分隨緣安本位，
自無煩惱在心前。', '江東孫策。象徵成敗皆有因緣不可過度強求，做好本分隨遇而安，自能無牽無掛。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 28, '第二十八籤 丙辛', '下下', '公私事務兩相催，
步步前進苦自隨。
退步思量且安坐，
莫將大事自磋跎。', '司馬相如客蜀。象徵內外交迫疲於奔命，盲目衝刺只會加劇內耗，宜停下腳步重整策略。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 29, '第二十九籤 丙壬', '上吉', '祖宗積德幾多年，
源遠流長福自綿。
若問前程名利事，
自然成就喜雙全。', '司馬懿破八陣。象徵基業與德行底蘊深厚，順理成章必有收穫，名利雙收水到渠成。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 30, '第三十籤 丙癸', '中吉', '奉公守法自然安，
何必旁人說短長。
若得貴人相引導，
自然門戶現光芒。', '柳毅傳書。象徵行事光明正大恪守正道，自有正義之士施以援手，迎向璀璨前程。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 31, '第三十一籤 丁甲', '中平', '秋冬作事只尋常，
春色微茫大吉昌。
莫向迷途深處走，
回頭便是好時光。', '蘇東坡赤壁懷古。象徵當前成效平平但春意已微露，及時矯正方向即可迎來大吉。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 32, '第三十二籤 丁乙', '下下', '萬事勞勞未見功，
營求奔走總成空。
如今且守波濤靜，
免使身心受折磨。', '周瑜赤壁破曹操。象徵勞碌奔波暫無回報，強行作為反增損耗，宜靜待局勢沉澱。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 33, '第三十三籤 丁丙', '中吉', '不須疑慮莫徬徨，
直道行來吉自昌。
若得貴人相引領，
自然步步入康莊。', '莊子破瓢。象徵去除多餘疑惑坦蕩前行，秉持正道必有貴人引導走向康莊大道。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 34, '第三十四籤 丁丁', '中平', '春夏作事未能成，
秋冬謀望得亨通。
如今且守安居樂，
待得良時吉慶生。', '張儀相秦。象徵時令季節未至不可勉強，安心蓄力到後半程，自然事事通達。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 35, '第三十五籤 丁戊', '下下', '一事無成心自焦，
門前雀鳥亦喧囂。
若非修善祈神庇，
安得災消福自招。', '王昭君出塞。象徵處於焦慮與困頓交織之際，當以內在修養與善念平息心火，切忌病急亂投醫。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 36, '第三十六籤 丁己', '上吉', '五十功名心已灰，
那知富貴逼人來。
更添福祿壽康寧，
門外喜迎旌節開。', '謝安東山再起。象徵即使過往心灰意冷，時來運轉之際富貴福澤依然主動降臨，晚景大開。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 37, '第三十七籤 丁庚', '中平', '事逢難處莫憂煎，
隨分隨緣且自然。
待得清光重照耀，
依然風景滿前川。', '邵堯夫觀物。象徵面對難題保持平常心，烏雲散去之時自然又是一番明媚景象。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 38, '第三十八籤 丁辛', '下下', '營求動作苦奔馳，
何日方能得自持。
且向家中安分坐，
莫教惹起禍殃基。', '孟姜女尋夫。象徵疲於奔命勞而少獲，宜回歸本位安居修身，勿輕舉妄動。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 39, '第三十九籤 丁壬', '下下', '日落西山暮氣深，
長途跋涉更何尋。
勸君及早尋歸路，
免教迷失枉用心。', '陶淵明歸隱。象徵大勢已暮不可強求進取，及早轉型或回歸本心方為上策。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 40, '第四十籤 丁癸', '上吉', '新來好事倍前番，
富貴榮華自此安。
若問功名並財利，
門庭吉慶喜相看。', '漢高祖斬蛇起義。象徵開創新局氣勢如虹，好事連連名利皆安。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 41, '第四十一籤 戊甲', '中吉', '自幼讀書志氣高，
如今方得遇英豪。
直上青雲千萬里，
不負當年鐵硯磨。', '劉備取荊州。象徵長期積累的底蘊終於遇見知音夥伴，一飛沖天。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 42, '第四十二籤 戊乙', '中吉', '我曾許汝事亨通，
誰料中途遇逆風。
好把舟航重整頓，
免教漂泊在江中。', '董永遇仙。象徵中途遇阻需立即重整旗鼓修補漏洞，切勿放任漂流。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 43, '第四十三籤 戊丙', '中平', '休說當年苦與辛，
如今且得作新民。
若能改過從善道，
自有天公暗助人。', '韓信拜將。象徵揮別過往辛酸，改頭換面行正道，自有天助。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 44, '第四十四籤 戊丁', '中吉', '門庭清吉事皆安，
何必旁人論短長。
若能知足隨緣過，
便是人間富貴鄉。', '孫叔敖斬蛇。象徵知足常樂心安理得，不為外境是非所動自享大福。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 45, '第四十五籤 戊戊', '中平', '好把身心全放下，
莫向名利苦營求。
隨緣守分安生理，
自無煩惱在心頭。', '高鳳自隱。象徵放下過度名利執念，順應日常生活自有平安安樂。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 46, '第四十六籤 戊己', '中平', '孤舟得水正相宜，
萬里鵬程在此時。
若得貴人相引領，
自然榮顯步丹墀。', '趙子龍救主。象徵孤舟得水時機正好，得力相助下前程開闊。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 47, '第四十七籤 戊庚', '下下', '年來作事苦奔馳，
到底營求總未奇。
如今且守安身計，
莫向旁人說是非。', '楚霸王垓下受困。象徵四面受挫宜止損守成，保全實力為要。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 48, '第四十八籤 戊辛', '中吉', '登山涉水正逢春，
步步前程草木新。
若問功名並財利，
自然成就見精神。', '趙匡胤借兵。象徵春回大地步步生機，付諸行動必見精神與成效。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 49, '第四十九籤 戊壬', '下下', '彼此何須苦競爭，
眼前萬事總由命。
退步思量且安坐，
免使身心受折騰。', '張良辭官。象徵競爭只會增加內耗，及時退一步保全自在人生。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 50, '第五十籤 戊癸', '上吉', '人說今年勝舊年，
家門和順福無邊。
若問求謀諸般事，
自然稱意樂安然。', '郭子儀滿床笏。象徵萬事順遂超越過往，家和萬事興稱心如意。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 51, '第五十一籤 己甲', '上吉', '君今百事且隨緣，
水到渠成不必牽。
若問前程名利事，
自然喜慶在眼前。', '禦溝流紅葉。象徵因緣俱足自然成事，不需焦慮拉扯，喜慶自來。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 52, '第五十二籤 己乙', '上吉', '作事須知有始終，
莫教半路自落空。
若能堅守初心志，
自然福祿永無窮。', '匡衡鑿壁。象徵有始有終堅持初心，勤勉自得深遠福祿。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 53, '第五十三籤 己丙', '中吉', '艱難歷盡見亨通，
雨後晴天日正中。
若問前程諸事業，
欣欣向榮樂融融。', '劉智遠投軍。象徵苦盡甘來雨過天晴，各項事業欣欣向榮。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 54, '第五十四籤 己丁', '中平', '萬人叢裡呈英豪，
便欲乘風上九霄。
若問前程名利事，
須防暗箭莫心驕。', '蘇秦配相印。象徵風光得意之際切記謙遜戒驕，防範潛在危機。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 55, '第五十五籤 己戊', '中平', '勤儉持家自有名，
莫向旁人說是非。
好把身心全放下，
神明自必暗相隨。', '包龍圖斷案。象徵勤儉自守遠離是非，天道自然暗中庇蔭。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 56, '第五十六籤 己己', '下下', '心事重重未得舒，
眼前迷霧罩長途。
勸君且退深思省，
免教惹禍自相殘。', '袁紹敗官渡。象徵迷惘與執念招致敗局，當深切反省及時止血。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 57, '第五十七籤 己庚', '中吉', '事無大小總宜防，
莫把閑言掛肚腸。
若得貴人相引導，
自然步步入康莊。', '嚴子陵垂釣。象徵謹慎防範莫受閒言干擾，得良友引導邁入康莊。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 58, '第五十八籤 己辛', '上吉', '千辛萬苦已成功，
回首前程大不同。
富貴榮華天付汝，
更添福祿在門中。', '蘇秦榮歸。象徵歷經考驗終獲大成，回首過往皆成榮耀養分。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 59, '第五十九籤 己壬', '中平', '門庭清吉免招憂，
勸君守分隨緣過。
若問功名謀望事，
寬心且看月中春。', '賈復歸光武。象徵守分安分即可免禍，靜候良機自然明朗。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 60, '第六十籤 己癸', '上吉', '羨君名利兩雙全，
萬里鵬程在眼前。
若得貴人相引領，
自然榮顯步青天。', '宋公明受招安。象徵名利俱全前程遠大，貴人引領直上青雲。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 61, '第六十一籤 庚甲', '中吉', '日出東方照四方，
陰霾散盡見晴光。
前途此去皆如意，
富貴榮華自吉昌。', '蒯輒見韓信。象徵日出東方驅散陰霾，前程明朗大有可為。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 62, '第六十二籤 庚乙', '中平', '作事何須苦自疑，
隨緣守分待良時。
若逢風虎雲龍會，
便是人生得意時。', '韓信遇蕭何。象徵勿自我懷疑，安分等待龍虎交會的契機展現自我。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 63, '第六十三籤 庚丙', '中吉', '求謀動作用功夫，
莫向旁人問有無。
只要心中存正念，
自然福祿在門庭。', '白居易登第。象徵下足真功夫自立自強，心存正念福祿自來。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 64, '第六十四籤 庚丁', '下下', '事到公庭各有傷，
爭名奪利苦心腸。
早把身心全放下，
免教惹得是非長。', '管鮑分金。象徵爭名奪利必生嫌隙，退讓釋懷才能保全情義。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 65, '第六十五籤 庚戊', '上吉', '碩果纍纍滿樹頭，
今年秋色大豐收。
士農工商皆稱意，
富貴榮華樂優遊。', '陶朱公致富。象徵經營得法碩果豐收，各方通達享受富足生活。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 66, '第六十六籤 庚己', '上吉', '耕耘深厚自豐盈，
萬事逢春漸見成。
若問前程名利事，
自然喜氣溢門楣。', '張騫通西域。象徵開拓格局深耕細作，春暖花開終獲厚報。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 67, '第六十七籤 庚庚', '中平', '世事茫茫未可期，
且向家中自整持。
若得良時並吉日，
自然謀望各相宜。', '江東二喬。象徵局勢未明時整理好內在與家庭，等待吉日良時。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 68, '第六十八籤 庚辛', '中吉', '君是山中大木材，
棟樑之器待時來。
如今且守安居樂，
直上青雲見帝台。', '錢塘重修。象徵棟樑之材勿憂無用，養精蓄銳即將受重用。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 69, '第六十九籤 庚壬', '下下', '一事無成惹是非，
眼前迷霧路多歧。
勸君及早尋歸路，
莫教身心受累危。', '孫臏被刖。象徵處境險惡是非纏身，應及早轉移退守防範暗算。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 70, '第七十籤 庚癸', '中吉', '雷雨風雲各及時，
如今作事莫遲疑。
若能把握好機會，
便是人間得意期。', '王曾得中三元。象徵天時地利俱備，當機立斷果決行動必創佳績。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 71, '第七十一籤 辛甲', '中平', '喜逢良夜月正明，
前途光耀步平生。
雖然小阻無大礙，
終見清光萬里清。', '蘇武牧羊。象徵雖有小阻礙但前途大體光明，坦蕩行事自無憂。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 72, '第七十二籤 辛乙', '下下', '公私多故惹憂煎，
步步前行苦自纏。
退步思量且安坐，
莫將大事自磋跎。', '范蠡退隱。象徵事務繁雜內耗過甚，及時抽身方能保全清寧。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 73, '第七十三籤 辛丙', '下下', '春雷震起未成霖，
欲向青雲少力尋。
且在深山修德行，
待逢良運便稱心。', '王祥臥冰。象徵實力尚未完備聲勢虛浮，宜深修內功等待時機。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 74, '第七十四籤 辛丁', '上吉', '崔巍獨步向青雲，
玉殿傳呼第一人。
富貴榮華天付汝，
福如東海壽如山。', '竇禹鈞折桂。象徵厚積薄發登峰造極，榮華福壽皆至。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 75, '第七十五籤 辛戊', '中吉', '生前積德幾多年，
今日家門福自延。
若問求謀諸事業，
自然稱意樂安然。', '劉寬恕下。象徵平日仁厚待人積下福澤，事業謀望自然順遂。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 76, '第七十六籤 辛己', '中平', '三千法律八百條，
作事循規莫動搖。
若能守法安身命，
自無煩惱在心頭。', '蕭何定律。象徵嚴守法規與紀律，循規蹈矩方能安穩長久。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 77, '第七十七籤 辛庚', '下下', '木雕泥塑枉勞神，
若是無緣莫苦求。
早把身心全放下，
免教惹禍自相仇。', '呂后害韓信。象徵緣分已盡不可強求，執迷不悟只會招惹災禍。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 78, '第七十八籤 辛辛', '下下', '家門不睦惹是非，
骨肉相爭苦自隨。
若能各讓三分地，
自然消散見春暉。', '袁紹兄弟相爭。象徵內部矛盾引發危機，唯有各退一步和解方有出路。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 79, '第七十九籤 辛壬', '中平', '乾坤定位自安然，
何必營求苦掛牽。
隨分隨緣安本位，
自無煩惱在心前。', '宋神宗即位。象徵順應客觀規律定位，安分守己自得安寧。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 80, '第八十籤 辛癸', '中吉', '一朝風月正精神，
萬里前程草木新。
若問功名並財利，
自然成就喜相親。', '陶侃運甓。象徵持之以恆磨練心志，時來運轉前程萬里。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 81, '第八十一籤 壬甲', '中吉', '白日青天照四方，
何須疑慮苦思量。
坦然大道平如掌，
任爾前行吉自昌。', '寇準秉政。象徵局勢大白光明磊落，放心闊步向前必得昌盛。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 82, '第八十二籤 壬乙', '上吉', '彼亦儔中一輩人，
何須自苦暗傷神。
如今且得通亨路，
直上青雲見日新。', '宋仁宗登極。象徵自信自重莫自卑，天寬地闊正是大展長才之時。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 83, '第八十三籤 壬丙', '下下', '隨分堂前赴鹿鳴，
何須枉費苦營求。
眼前富貴如雲霧，
散去空中總成空。', '諸葛孔明病逝。象徵浮華名利如過眼雲煙，勿過度執念勞損心神。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 84, '第八十四籤 壬丁', '中平', '青天霹靂震山川，
轉瞬風平浪更恬。
莫把暫時風浪怕，
平安到底慶團圓。', '趙子龍破曹軍。象徵短暫震盪不用驚慌，風雨過後自然平安團圓。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 85, '第八十五籤 壬戊', '中吉', '一春萬事正逢時，
草木萌芽發自奇。
若問前程名利事，
欣欣向榮樂無疑。', '姜子牙遇文王。象徵春意盎然萬物復甦，此時展開行動必有收穫。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 86, '第八十六籤 壬己', '上吉', '一樹桃花滿院紅，
春來生意大亨通。
若問前程謀望事，
自然成就見成功。', '管仲相齊桓公。象徵時機成熟生意盎然，所謀之事必能成功。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 87, '第八十七籤 壬庚', '下下', '獨占鰲頭未得伸，
眼前迷霧路多迍。
勸君及早尋歸計，
免教惹禍自相焚。', '石崇被殺。象徵驕奢與執念引火上身，及早退讓自救為上。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 88, '第八十八籤 壬辛', '上吉', '從前作事苦憂煎，
今日欣逢好運連。
富貴榮華天付汝，
門前喜氣溢雙全。', '漢高祖還鄉。象徵苦盡甘來好運連連，榮耀回歸喜氣洋洋。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 89, '第八十九籤 壬壬', '中吉', '平生志氣薄雲霄，
今日方知造化巧。
若得貴人相引導，
自然步步上青雲。', '班超立功異域。象徵雄心壯志遇得良機，貴人提攜直上青雲。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 90, '第九十籤 壬癸', '中平', '奉公守法免憂煎，
隨分隨緣且自然。
待得清光重照耀，
依然風景滿前川。', '楊震拒金。象徵廉潔自律不欺暗室，光明磊落自得善報。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 91, '第九十一籤 癸甲', '中吉', '佛說靈籤最吉昌，
前程此去得安康。
若問功名並財利，
自然成就有榮光。', '趙子龍斬五將。象徵神清氣定無所畏懼，過關斬將終得榮耀。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 92, '第九十二籤 癸乙', '下下', '今年運勢苦難通，
營求奔走總成空。
如今且守波濤靜，
免教惹禍在身中。', '富貴無常。象徵運勢不順徒勞無功，守靜防守以防意外。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 93, '第九十三籤 癸丙', '中平', '春蠶作繭自纏綿，
何苦身心受困牽。
若能打破堅牢網，
化作彩蝶上九天。', '莊子破繭。象徵打破自我設限與心靈枷鎖，蛻變重生展翅高飛。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 94, '第九十四籤 癸丁', '中吉', '若問前程得路通，
寬心且等待春風。
如今且守波濤靜，
待得良時吉慶重。', '伍子胥復仇。象徵隱忍沉著等待東風，關鍵時刻必定翻轉。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 95, '第九十五籤 癸戊', '中平', '門庭清吉免招憂，
勸君守分隨緣過。
命中註定無偏差，
會有榮華富貴誇。', '張良隱退。象徵守分隨緣順應天時，無欲則剛自有清福。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 96, '第九十六籤 癸己', '上吉', '幸有神仙來引路，
前程此去得亨通。
若問功名並財利，
榮華富貴樂無窮。', '漢明帝求佛法。象徵得高人指引開創新局，智慧通達福祿長久。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 97, '第九十七籤 癸庚', '大吉', '五十功名心已灰，
那知富貴逼人來。
更添福祿壽康寧，
門外喜迎旌節開。', '宋太祖受禪。象徵大器晚成好運逼人，福壽雙全吉慶連綿。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 98, '第九十八籤 癸辛', '中平', '公私多故惹憂煎，
步步前行苦自隨。
退步思量且安坐，
莫將大事自磋跎。', '薛仁貴征東歸。象徵適時止步重整旗鼓，退一步思考方成大事。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 99, '第九十九籤 癸壬', '上吉', '貴人引領步青雲，
萬里鵬程在此間。
富貴榮華天付汝，
更添福祿在門前。', '百里奚相秦。象徵良師益友鼎力相助，前程萬里開拓宏圖。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guandi_100', '關聖帝君一百籤', 100, '第一百籤 癸癸', '大吉', '我本天仙雷雨師，
吉凶禍福我先知。
至誠禱告皆能應，
萬事亨通福壽齊。', '雷雨師聖訓。象徵誠心正念感動天地，圓滿無礙萬事亨通。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 1, '第一籤', '上上', '開天闢地作良緣，
吉日良時度本全。
若得此籤非小可，
人居泰運福綿綿。', '鍾馗得道。象徵開天闢地萬象更新，吉日良時福祿綿延，宏圖大展。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 2, '第二籤', '下下', '鯨鯢已化鶴飛天，
一任飄搖直上仙。
遇鼠逢牛三弄笛，
好將名姓表金榜。', '蘇秦不第。象徵暫時受挫懷才不遇，宜沉潛蓄力等待時機方能一展抱負。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 3, '第三籤', '下下', '臨風冒雨去還鄉，
正是倉皇抵死場。
幸得長途平浪穩，
扁舟又過短蓬窗。', '董永賣身。象徵身處逆境風雨交加，但只要心存誠孝正直，終能度過危難迎來平穩。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 4, '第四籤', '上上', '千年古鏡復重圓，
女再求夫男再婚。
自此門庭重改換，
更添福祿在兒孫。', '玉鏡重圓。象徵破鏡重圓缺憾彌補，家道重光帶來全新氣象與後代福報。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 5, '第五籤', '中平', '一錐草地要求圓，
料得姻緣難稱意。
若是兩家同合好，
自然終久得平安。', '劉晨遇仙。象徵求全責備反增煩惱，多方包容互相協調，自然長久平安。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 6, '第六籤', '中平', '投身岩下飼於菟，
須是請君用心機。
若是得逢存保佑，
自然吉慶免災危。', '仁貴投軍。象徵歷經險境艱難求生，需謹慎應對運用智慧，得貴人護佑化險為夷。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 7, '第七籤', '下下', '奔波役役所為何，
勞祿身心未自和。
退步思量且安坐，
莫將大事自磋跎。', '蘇娘走難。象徵勞碌奔波內外交困，宜停下腳步深思反省，切勿盲動自誤大事。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 8, '第八籤', '上上', '茂林修竹映長流，
芳草連天景色悠。
若得知音同賞玩，
一生清福有何求。', '裴度還帶。象徵心存善念福蔭深厚，得遇良伴共賞人生風景，享受清靜大福。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 9, '第九籤', '上上', '勞君問卜借神明，
目前暗昧未澄清。
休聽旁人說是非，
自得身安免禍殃。', '孔明練兵。象徵局勢未明之際需專注自身實力沉澱，莫聽閒言雜語自得安泰。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 10, '第十籤', '中平', '寶雕金字號朝天，
萬里鵬程在此宣。
若問前程謀望事，
自然得利免憂煎。', '龐涓觀陣。象徵具備才華抱負，但需戒除驕躁嫉妒，踏實前行自能得利。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 11, '第十一籤', '上上', '德業修成自不同，
清光朗照大明中。
若問前程名利事，
欣欣向榮樂融融。', '韓文公登第。象徵德業兼修實力雄厚，前程一片光明如日中天。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 12, '第十二籤', '上吉', '否極泰來日正長，
榮華富貴好風光。
若能堅守初心志，
自然門戶自芬芳。', '包公審烏盆。象徵冤屈昭雪否極泰來，堅持正道初心終獲榮耀。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 13, '第十三籤', '中平', '自小生來命薄微，
前途多難事相違。
如今且守安身計，
待得良時吉慶隨。', '羅通掃北。象徵早年多磨難，當前宜厚植實力守安分，待時運轉化。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 14, '第十四籤', '大吉', '宛如靈鶴出樊籠，
脫卻羈絆上碧空。
一任東西南北去，
逍遙自在樂無窮。', '子牙得道。象徵擺脫長期束縛展翅高飛，天地寬廣逍遙自在。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 15, '第十五籤', '中平', '雀噪鳩鳴事不真，
何須苦苦用心神。
只要自己存公道，
免得旁人論是非。', '張飛斷橋。象徵外在流言蜚語不攻自破，心中秉持公正自能無懼是非。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 16, '第十六籤', '上上', '愁雲散盡見青天，
萬里山河在眼前。
若問前程名利事，
欣然得意自團圓。', '葉夢熊朝帝。象徵愁雲散去晴空萬里，前程開展名利皆順。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 17, '第十七籤', '中平', '莫聽旁人說是非，
眼前迷霧路多歧。
勸君守定身心志，
自得平安免是非。', '話墮為投機。象徵歧路甚多需守定心志，遠離是非流言以保平安。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 18, '第十八籤', '上吉', '金烏西墜兔東升，
日夜循環步步登。
若得貴人相引領，
自然富貴喜重增。', '曹國舅得道。象徵遵循自然規律日夜精進，得貴人提攜富貴重增。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 19, '第十九籤', '中平', '急水灘頭放下船，
竿頭須要用機關。
若逢急處須當退，
免使身心受折磨。', '子胥過江。象徵處於湍急險境需機智應變，適時退讓避開危險。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 20, '第二十籤', '中平', '當春久雨喜初晴，
玉兔金烏漸漸明。
舊事已消新事起，
前程從此得安寧。', '姜太公遇文王。象徵久雨初晴舊事翻篇，嶄新階段自此步入正軌。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 21, '第二十一籤', '上上', '陰陽道合總由天，
女嫁男婚喜自然。
但把身心全放下，
榮華富貴得雙全。', '李旦鳳閣重圓。象徵天作之合順應自然，放下焦慮自得圓滿與福貴。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 22, '第二十二籤', '中平', '四郊田疇大有秋，
士農工商樂優遊。
若能常存忠信志，
自然門戶足無憂。', '王孝先為民祈雨。象徵誠意感天田產豐收，心存忠信萬事無憂。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 23, '第二十三籤', '中平', '欲求富貴莫心急，
且向深山好整齊。
待得春來草木發，
自然門戶得安怡。', '懷德招親。象徵欲速則不達，當下整理自我，春風一吹自得安樂。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 24, '第二十四籤', '下下', '不須作事苦奔馳，
前路迷茫未可知。
且向家中安分坐，
莫教惹起禍殃基。', '殷郊遇難。象徵前路迷霧重重切忌冒進，安分守己防範災殃。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 25, '第二十五籤', '中平', '過了憂危事事通，
寬懷且看夕陽紅。
如今若問前程事，
貴人指引步青雲。', '趙子龍救主。象徵度過最危險時刻後萬事通達，貴人接引步上青雲。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 26, '第二十六籤', '上吉', '上下和睦事皆通，
家道興隆樂意融。
若問前程諸事業，
欣欣向榮福無窮。', '鐘馗得道。象徵內外團結家和萬事興，事業欣欣向榮福澤無窮。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 27, '第二十七籤', '中平', '一事無成心自焦，
門前雀鳥亦喧囂。
若非修善祈神庇，
安得災消福自招。', '劉晨阮肇入天台。象徵面對繁雜干擾需靜修善念，心安定則災消福來。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 28, '第二十八籤', '上上', '東方破曉日重升，
萬里山川景色新。
若問功名並財利，
自然成就見精神。', '孟嘗君收債。象徵破曉迎新局面，豁達大度必獲豐厚回饋。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 29, '第二十九籤', '中平', '寶劍出匣耀光明，
在握威風四海驚。
若得英雄齊助力，
自然步步建奇功。', '趙子龍長坂坡。象徵鋒芒初露展現實力，得眾人合力必建奇功。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 30, '第三十籤', '中吉', '勸君作事莫心焦，
且待春風引路橋。
若得良時並吉日，
自然福祿在門楣。', '楚懷王入秦。象徵行事沉得住氣等待東風，吉日良時自得福祿。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 31, '第三十一籤', '中吉', '清閒無事自然安，
何必旁人說短長。
若得貴人相引薦，
自然門戶現光芒。', '佛印與東坡。象徵內心清閒安泰不受擾，得高人引薦光芒自現。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 32, '第三十二籤', '下下', '作事須知防後患，
莫教大意失荊州。
退步思量且安坐，
免使身心受折磨。', '關羽失荊州。象徵切忌因大意驕矜而留下破綻，宜嚴加防範退步自省。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 33, '第三十三籤', '中吉', '石藏美玉未逢時，
且在深山自整持。
待得良工來剖琢，
自然光彩奪人知。', '卞和獻玉。象徵才華如美玉蘊藏於石，耐得住寂寞等待伯樂雕琢。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 34, '第三十四籤', '中平', '行舟涉水遇狂風，
舵正帆齊不怕衝。
只要心中存定力，
自然平安過江東。', '孫權保江東。象徵面對風浪只要把穩方向堅定信念，必能安渡險灘。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 35, '第三十五籤', '上吉', '衣冠整齊拜朝廷，
富貴榮華自此生。
若問前程名利事，
欣然得意受恩榮。', '蘇秦拜相。象徵衣錦還鄉榮耀加身，努力終得最高肯定。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 36, '第三十六籤', '中平', '雀入籠中難展翅，
且向安樂守身家。
待得春來開籠日，
自然飛上碧天霞。', '相如客蜀。象徵暫受環境限制難以發揮，安分休養待開籠之日。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 37, '第三十七籤', '中吉', '欲問前程不必疑，
隨緣守分待良時。
若逢風虎雲龍會，
便是人生得意期。', '管仲遇桓公。象徵放下焦慮隨緣守分，龍虎相會時機至自顯身手。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 38, '第三十八籤', '下下', '月下追尋未見蹤，
舟行逆水苦難通。
如今且守波濤靜，
免使身心受折衝。', '何仙姑度韓湘子。象徵逆境追尋徒增疲憊，守靜蓄力方能保身。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 39, '第三十九籤', '下下', '天邊消息未分明，
眼前迷霧路多程。
勸君及早尋歸路，
免教身心受累驚。', '姜女尋夫。象徵訊息未明不可冒險追逐，及早轉身避免徒勞驚險。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 40, '第四十籤', '中吉', '紅日當空四海明，
前途光耀步平生。
若問功名並財利，
自然成就慶雙榮。', '武則天稱帝。象徵如日中天光芒四射，把握時運成就非凡事業。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 41, '第四十一籤', '中平', '無限風光在眼前，
何須苦苦去爭先。
隨分隨緣安本位，
自然清福樂綿綿。', '董卓入洛陽。象徵珍惜眼前美好不搶急功，守分安居自享清福。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 42, '第四十二籤', '上吉', '君是山中大棟樑，
青雲直上出家鄉。
若能堅守初心志，
自然名利自芬芳。', '諸葛孔明出廬。象徵棟樑之器大展宏圖，不忘初心終建千秋偉業。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 43, '第四十三籤', '上吉', '天地同心萬物春，
欣欣向榮百花新。
若問前程謀望事，
自然成就見精神。', '泗水亭長得天下。象徵順應天時人心所向，萬物復甦大有可為。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 44, '第四十四籤', '中吉', '棋逢敵手細思量，
莫教大意失商量。
若能審慎行棋步，
自見乾坤日月長。', '姜尚渭水釣魚。象徵面對強勁局勢需步步為營審慎佈局，方得長遠勝利。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 45, '第四十五籤', '中平', '一春萬事苦憂煎，
夏裡營求亦未全。
秋至冬來多阻礙，
不如且退保身全。', '仁宗認母。象徵考驗尚未完全退去，以穩健防守保全實力為要。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 46, '第四十六籤', '中吉', '勤儉自持萬事興，
門庭和睦樂融融。
若問前程名利事，
自然福祿在其中。', '渭水逢文王。象徵勤勉自持修睦人際，福祿自然水到渠成。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 47, '第四十七籤', '上上', '日出東方萬里明，
前程此去得通亨。
若問功名並財利，
自然成就喜相迎。', '高祖斬蛇。象徵曙光萬丈驅散陰霾，闊步向前必有喜慶相迎。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 48, '第四十八籤', '中吉', '登山涉水好春光，
萬里鵬程在此方。
若得貴人相指引，
自然步步入康莊。', '韓信拜將。象徵春光正好大膽探索，貴人指引下邁入康莊坦途。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 49, '第四十九籤', '中平', '彼此何須苦競爭，
眼前萬事總由命。
退步思量且安坐，
免使身心受折騰。', '太子丹別荊軻。象徵無謂相爭徒增內耗，適時退一步海闊天空。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 50, '第五十籤', '上吉', '五湖四海任遨遊，
萬里鵬程得意秋。
若得貴人齊助力，
自然富貴樂優遊。', '陶朱公遊五湖。象徵格局宏大四海通達，得眾人相助富足自在。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 51, '第五十一籤', '上吉', '初出深山第一枝，
春來生意正相宜。
若問前程名利事，
自然欣欣樂自知。', '孔明入川。象徵初露鋒芒春意正濃，前程開闊喜樂自知。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 52, '第五十二籤', '中平', '作事須知有始終，
莫教半路自成空。
若能堅守初心志，
自然福祿永無窮。', '鮑叔牙薦管仲。象徵善始善終堅持初心，誠懇相待福祿綿延。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 53, '第五十三籤', '中吉', '艱難歷盡見亨通，
雨後晴天日正中。
若問前程諸事業，
欣欣向榮樂融融。', '劉智遠投軍。象徵歷盡艱辛迎來開闊，各項事業欣欣向榮。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 54, '第五十四籤', '下下', '風雲突變起波瀾，
舟行急處莫心歡。
勸君及早收帆楫，
免教漂泊在狂瀾。', '馬謖失街亭。象徵局勢驟變切勿大意，及早收斂防守以保平安。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 55, '第五十五籤', '中吉', '祖宗積德有餘慶，
家門和順自安康。
若問求謀諸般事，
自然稱意樂無疆。', '周武王伐紂。象徵積善之家必有餘慶，順應天理所求如意。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 56, '第五十六籤', '中平', '心事重重未得舒，
眼前迷霧罩長途。
勸君且退深思省，
免教惹禍自相殘。', '范蠡退隱。象徵心結未開時莫急於做決定，退步深思方能免禍。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 57, '第五十七籤', '上吉', '事無大小總宜防，
莫把閑言掛肚腸。
若得貴人相引導，
自然步步入康莊。', '董永遇仙。象徵謹慎應對莫理閒言，貴人引領走向康莊。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 58, '第五十八籤', '上吉', '千辛萬苦已成功，
回首前程大不同。
富貴榮華天付汝，
更添福祿在門中。', '蘇秦封相。象徵苦盡甘來大功告成，榮華富貴天道有知。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 59, '第五十九籤', '中平', '門庭清吉免招憂，
勸君守分隨緣過。
若問功名謀望事，
寬心且看月中春。', '張良得兵書。象徵守分安分等待時節，良機到來自然通達。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 60, '第六十籤', '上吉', '羨君名利兩雙全，
萬里鵬程在眼前。
若得貴人相引領，
自然榮顯步青天。', '宋太祖登極。象徵名利兼備前程似錦，得道多助直上青天。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 61, '第六十一籤', '中平', '日出東方照四方，
陰霾散盡見晴光。
前途此去皆如意，
富貴榮華自吉昌。', '平貴回窯。象徵日出破霾光明在望，堅持到底迎來圓滿。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 62, '第六十二籤', '中吉', '作事何須苦自疑，
隨緣守分待良時。
若逢風虎雲龍會，
便是人生得意時。', '韓信破齊。象徵切莫自我懷疑，把握龍虎會合良機展翅高飛。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 63, '第六十三籤', '中吉', '求謀動作用功夫，
莫向旁人問有無。
只要心中存正念，
自然福祿在門庭。', '白居易登第。象徵下足真功夫自立自強，心存正念福祿自來。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 64, '第六十四籤', '下下', '事到公庭各有傷，
爭名奪利苦心腸。
早把身心全放下，
免教惹得是非長。', '管鮑分金。象徵爭名奪利必生嫌隙，退讓釋懷才能保全情義。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 65, '第六十五籤', '上吉', '碩果纍纍滿樹頭，
今年秋色大豐收。
士農工商皆稱意，
富貴榮華樂優遊。', '陶朱公致富。象徵經營得法碩果豐收，各方通達享受富足生活。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 66, '第六十六籤', '上吉', '耕耘深厚自豐盈，
萬事逢春漸見成。
若問前程名利事，
自然喜氣溢門楣。', '張騫通西域。象徵開拓格局深耕細作，春暖花開終獲厚報。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 67, '第六十七籤', '中平', '世事茫茫未可期，
且向家中自整持。
若得良時並吉日，
自然謀望各相宜。', '江東二喬。象徵局勢未明時整理好內在與家庭，等待吉日良時。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 68, '第六十八籤', '中吉', '君是山中大木材，
棟樑之器待時來。
如今且守安居樂，
直上青雲見帝台。', '錢塘重修。象徵棟樑之材勿憂無用，養精蓄銳即將受重用。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 69, '第六十九籤', '下下', '一事無成惹是非，
眼前迷霧路多歧。
勸君及早尋歸路，
莫教身心受累危。', '孫臏被刖。象徵處境險惡是非纏身，應及早轉移退守防範暗算。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 70, '第七十籤', '中吉', '雷雨風雲各及時，
如今作事莫遲疑。
若能把握好機會，
便是人間得意期。', '王曾得中三元。象徵天時地利俱備，當機立斷果決行動必創佳績。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 71, '第七十一籤', '中平', '喜逢良夜月正明，
前途光耀步平生。
雖然小阻無大礙，
終見清光萬里清。', '蘇武牧羊。象徵雖有小阻礙但前途大體光明，坦蕩行事自無憂。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 72, '第七十二籤', '下下', '公私多故惹憂煎，
步步前行苦自纏。
退步思量且安坐，
莫將大事自磋跎。', '范蠡退隱。象徵事務繁雜內耗過甚，及時抽身方能保全清寧。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 73, '第七十三籤', '下下', '春雷震起未成霖，
欲向青雲少力尋。
且在深山修德行，
待逢良運便稱心。', '王祥臥冰。象徵實力尚未完備聲勢虛浮，宜深修內功等待時機。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 74, '第七十四籤', '上吉', '崔巍獨步向青雲，
玉殿傳呼第一人。
富貴榮華天付汝，
福如東海壽如山。', '竇禹鈞折桂。象徵厚積薄發登峰造極，榮華福壽皆至。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 75, '第七十五籤', '中吉', '生前積德幾多年，
今日家門福自延。
若問求謀諸事業，
自然稱意樂安然。', '劉寬恕下。象徵平日仁厚待人積下福澤，事業謀望自然順遂。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 76, '第七十六籤', '中平', '三千法律八百條，
作事循規莫動搖。
若能守法安身命，
自無煩惱在心頭。', '蕭何定律。象徵嚴守法規與紀律，循規蹈矩方能安穩長久。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 77, '第七十七籤', '下下', '木雕泥塑枉勞神，
若是無緣莫苦求。
早把身心全放下，
免教惹禍自相仇。', '呂后害韓信。象徵緣分已盡不可強求，執迷不悟只會招惹災禍。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 78, '第七十八籤', '下下', '家門不睦惹是非，
骨肉相爭苦自隨。
若能各讓三分地，
自然消散見春暉。', '袁紹兄弟相爭。象徵內部矛盾引發危機，唯有各退一步和解方有出路。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 79, '第七十九籤', '中平', '乾坤定位自安然，
何必營求苦掛牽。
隨分隨緣安本位，
自無煩惱在心前。', '宋神宗即位。象徵順應客觀規律定位，安分守己自得安寧。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 80, '第八十籤', '中吉', '一朝風月正精神，
萬里前程草木新。
若問功名並財利，
自然成就喜相親。', '陶侃運甓。象徵持之以恆磨練心志，時來運轉前程萬里。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 81, '第八十一籤', '中吉', '白日青天照四方，
何須疑慮苦思量。
坦然大道平如掌，
任爾前行吉自昌。', '寇準秉政。象徵局勢大白光明磊落，放心闊步向前必得昌盛。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 82, '第八十二籤', '上吉', '彼亦儔中一輩人，
何須自苦暗傷神。
如今且得通亨路，
直上青雲見日新。', '宋仁宗登極。象徵自信自重莫自卑，天寬地闊正是大展長才之時。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 83, '第八十三籤', '下下', '隨分堂前赴鹿鳴，
何須枉費苦營求。
眼前富貴如雲霧，
散去空中總成空。', '諸葛孔明病逝。象徵浮華名利如過眼雲煙，勿過度執念勞損心神。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 84, '第八十四籤', '中平', '青天霹靂震山川，
轉瞬風平浪更恬。
莫把暫時風浪怕，
平安到底慶團圓。', '趙子龍破曹軍。象徵短暫震盪不用驚慌，風雨過後自然平安團圓。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 85, '第八十五籤', '中吉', '一春萬事正逢時，
草木萌芽發自奇。
若問前程名利事，
欣欣向榮樂無疑。', '姜子牙遇文王。象徵春意盎然萬物復甦，此時展開行動必有收穫。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 86, '第八十六籤', '上吉', '一樹桃花滿院紅，
春來生意大亨通。
若問前程謀望事，
自然成就見成功。', '管仲相齊桓公。象徵時機成熟生意盎然，所謀之事必能成功。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 87, '第八十七籤', '下下', '獨占鰲頭未得伸，
眼前迷霧路多迍。
勸君及早尋歸計，
免教惹禍自相焚。', '石崇被殺。象徵驕奢與執念引火上身，及早退讓自救為上。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 88, '第八十八籤', '上吉', '從前作事苦憂煎，
今日欣逢好運連。
富貴榮華天付汝，
門前喜氣溢雙全。', '漢高祖還鄉。象徵苦盡甘來好運連連，榮耀回歸喜氣洋洋。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 89, '第八十九籤', '中吉', '平生志氣薄雲霄，
今日方知造化巧。
若得貴人相引導，
自然步步上青雲。', '班超立功異域。象徵雄心壯志遇得良機，貴人提攜直上青雲。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 90, '第九十籤', '中平', '奉公守法免憂煎，
隨分隨緣且自然。
待得清光重照耀，
依然風景滿前川。', '楊震拒金。象徵廉潔自律不欺暗室，光明磊落自得善報。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 91, '第九十一籤', '中吉', '佛說靈籤最吉昌，
前程此去得安康。
若問功名並財利，
自然成就有榮光。', '趙子龍斬五將。象徵神清氣定無所畏懼，過關斬將終得榮耀。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 92, '第九十二籤', '下下', '今年運勢苦難通，
營求奔走總成空。
如今且守波濤靜，
免教惹禍在身中。', '富貴無常。象徵運勢不順徒勞無功，守靜防守以防意外。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 93, '第九十三籤', '中平', '春蠶作繭自纏綿，
何苦身心受困牽。
若能打破堅牢網，
化作彩蝶上九天。', '莊子破繭。象徵打破自我設限與心靈枷鎖，蛻變重生展翅高飛。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 94, '第九十四籤', '中吉', '若問前程得路通，
寬心且等待春風。
如今且守波濤靜，
待得良時吉慶重。', '伍子胥復仇。象徵隱忍沉著等待東風，關鍵時刻必定翻轉。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 95, '第九十五籤', '中平', '門庭清吉免招憂，
勸君守分隨緣過。
命中註定無偏差，
會有榮華富貴誇。', '張良隱退。象徵守分隨緣順應天時，無欲則剛自有清福。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 96, '第九十六籤', '上吉', '幸有神仙來引路，
前程此去得亨通。
若問功名並財利，
榮華富貴樂無窮。', '漢明帝求佛法。象徵得高人指引開創新局，智慧通達福祿長久。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 97, '第九十七籤', '大吉', '五十功名心已灰，
那知富貴逼人來。
更添福祿壽康寧，
門外喜迎旌節開。', '宋太祖受禪。象徵大器晚成好運逼人，福壽雙全吉慶連綿。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 98, '第九十八籤', '中平', '公私多故惹憂煎，
步步前行苦自隨。
退步思量且安坐，
莫將大事自磋跎。', '薛仁貴征東歸。象徵適時止步重整旗鼓，退一步思考方成大事。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 99, '第九十九籤', '上吉', '貴人引領步青雲，
萬里鵬程在此間。
富貴榮華天付汝，
更添福祿在門前。', '百里奚相秦。象徵良師益友鼎力相助，前程萬里開拓宏圖。');
INSERT OR IGNORE INTO lots (lot_type, lot_type_name, lot_number, lot_name, grade, content, story) VALUES ('guanyin_100', '觀音靈籤一百首', 100, '第一百籤', '上上', '三教談道悟真詮，
萬里無雲碧滿天。
若得此籤非小可，
福如東海壽如山。', '三教談道。象徵融會貫通智慧圓滿，萬里無雲心境澄明，福壽綿長。');
