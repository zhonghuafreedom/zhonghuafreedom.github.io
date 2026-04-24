document.addEventListener('DOMContentLoaded', () => {
    // Language Toggle Logic
    const langToggleBtn = document.getElementById('lang-toggle');
    const body = document.body;

    // Check local storage or default to 'zh'
    const currentLang = localStorage.getItem('lang') || 'zh';
    setLanguage(currentLang);

    langToggleBtn.addEventListener('click', () => {
        const newLang = body.getAttribute('data-lang') === 'zh' ? 'en' : 'zh';
        setLanguage(newLang);
    });

    function setLanguage(lang) {
        body.setAttribute('data-lang', lang);
        localStorage.setItem('lang', lang);

        // Update button text
        langToggleBtn.textContent = lang === 'zh' ? 'EN / 中' : '中 / EN';
    }

    // Mobile Menu Toggle
    const mobileBtn = document.querySelector('.mobile-menu-btn');
    const nav = document.querySelector('.main-nav');

    mobileBtn.addEventListener('click', () => {
        nav.classList.toggle('active');
        mobileBtn.classList.toggle('active');
    });

    // Close menu when clicking a link
    document.querySelectorAll('.main-nav a').forEach(link => {
        link.addEventListener('click', () => {
            nav.classList.remove('active');
            mobileBtn.classList.remove('active');
        });
    });

    // Smooth Scrolling for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: "smooth"
                });
            }
        });
    });

    // Dynamic Reports Loader (Bilingual)
    const reportsGrid = document.getElementById('reports-grid');
    const reports = [
        {
            title_zh: "劉霞：詩人、囚徒、亡夫之妻",
            title_en: "Liu Xia: Poet, Prisoner, Widow of a Laureate",
            date: "2010-10-08",
            excerpt_zh: "諾貝爾和平獎得主劉曉波之妻劉霞，在丈夫獲獎後遭非法軟禁長達八年，她的詩與沉默成為中國良知的另一種記錄。",
            excerpt_en: "After her husband Liu Xiaobo was awarded the Nobel Peace Prize, poet Liu Xia was placed under illegal house arrest for nearly eight years. Her silence and verse became another testament to China's conscience.",
            url: "posts/liu-xia.html"
        },
        {
            title_zh: "艾未未：藝術作為抵抗",
            title_en: "Ai Weiwei: Art as Resistance",
            date: "2011-04-03",
            excerpt_zh: "從汶川遇難學生姓名牆到 81 天秘密拘留，艾未未用藝術揭露國家暴力，成為中共最知名的異議者之一。",
            excerpt_en: "From the Sichuan earthquake students' name wall to his 81-day secret detention, Ai Weiwei has used art to expose state violence, becoming one of the CCP's most renowned dissidents.",
            url: "posts/ai-weiwei.html"
        },
        {
            title_zh: "王全璋律師：709事件中失蹤的良知",
            title_en: "Lawyer Wang Quanzhang: A Conscience Disappeared in the 709 Crackdown",
            date: "2019-01-28",
            excerpt_zh: "709大抓捕中被秘密羈押逾三年的王全璋律師，是中國法治崩壞與「指定居所監視居住」制度的象徵。",
            excerpt_en: "Held incommunicado for over three years after the 709 Crackdown, lawyer Wang Quanzhang has come to symbolize China's collapsing rule of law and the abuse of 'Residential Surveillance at a Designated Location'.",
            url: "posts/wang-quanzhang.html"
        },
        {
            title_zh: "王炳章：被綁架的中國民運先驅",
            title_en: "Wang Bingzhang: The Kidnapped Founder of China's Overseas Democracy Movement",
            date: "2003-02-10",
            excerpt_zh: "海外中國民運奠基人王炳章2002年於越中邊境被綁架回中國，被秘密判處無期徒刑，至今仍在獄中。",
            excerpt_en: "Wang Bingzhang, founder of the overseas Chinese democracy movement, was kidnapped from the Vietnam-China border in 2002 and secretly sentenced to life imprisonment. He remains in prison today.",
            url: "posts/wang-bingzhang.html"
        },
        {
            title_zh: "陳光誠：盲人維權者的逃亡",
            title_en: "Chen Guangcheng: The Blind Activist Who Escaped",
            date: "2012-04-22",
            excerpt_zh: "盲人維權律師陳光誠揭發山東計劃生育暴力，遭4年監禁與7年軟禁，2012年戲劇性翻牆逃入美國駐華大使館。",
            excerpt_en: "Blind legal advocate Chen Guangcheng exposed the violence of family planning in Shandong. After 4 years in prison and 7 years of house arrest, he made a dramatic 2012 escape into the US Embassy in Beijing.",
            url: "posts/chen-guangcheng.html"
        },
        {
            title_zh: "銅鑼灣書店事件：跨境綁架的開端",
            title_en: "Causeway Bay Books: The Opening Act of Cross-Border Abduction",
            date: "2015-10-14",
            excerpt_zh: "2015年香港銅鑼灣書店五名股東與員工先後在港、深、泰失蹤，後出現於中國電視認罪，揭開中共跨境鎮壓序幕。",
            excerpt_en: "In 2015, five shareholders and staff of Hong Kong's Causeway Bay Books vanished from Hong Kong, Shenzhen, and Thailand—later appearing in televised confessions on Chinese state TV, opening Beijing's era of cross-border abduction.",
            url: "posts/causeway-bay-books.html"
        },
        {
            title_zh: "江天勇律師：被酷刑與直播認罪的維權者",
            title_en: "Lawyer Jiang Tianyong: Tortured and Forced into a Televised Confession",
            date: "2017-11-21",
            excerpt_zh: "維權律師江天勇在 709 案後仍堅持為被捕同行家屬奔走，2017 年被秘密審判並被迫電視認罪，揭露中國司法的黑箱。",
            excerpt_en: "Rights lawyer Jiang Tianyong continued to support families of detained 709 colleagues. In 2017 he was tried in secret and forced into a televised confession, exposing the black box of China's justice system.",
            url: "posts/jiang-tianyong.html"
        },
        {
            title_zh: "香港 47 人案：戰後最大規模政治審判",
            title_en: "The Hong Kong 47: The Largest Political Trial Since World War II",
            date: "2024-11-19",
            excerpt_zh: "2021 年 47 名香港民主派人士因參與初選被以「串謀顛覆」起訴，2024 年被判 4 至 10 年，創下香港殖民後最大規模政治審判。",
            excerpt_en: "In 2021, 47 Hong Kong democrats were charged with 'conspiracy to subvert' for taking part in a primary election. Sentenced in 2024 to between 4 and 10 years, theirs is the largest political trial in post-handover Hong Kong.",
            url: "posts/hk-47.html"
        },
        {
            title_zh: "廣州十二人案：偷渡海上的香港抗爭者",
            title_en: "The Hong Kong 12: Protesters Caught at Sea",
            date: "2020-12-30",
            excerpt_zh: "2020 年 12 名香港青年乘船赴台途中被中國海警截獲，秘密拘押於深圳鹽田，揭示跨境政治迫害的真實面貌。",
            excerpt_en: "In 2020, twelve young Hongkongers fleeing by speedboat to Taiwan were intercepted at sea by China Coast Guard and secretly held at Yantian, Shenzhen—exposing the reality of cross-border political persecution.",
            url: "posts/hk-12.html"
        },
        {
            title_zh: "豐縣「鐵鏈女」事件：被遺忘的拐賣婦女",
            title_en: "The 'Chained Woman' of Feng County: Trafficked Women China Forgot",
            date: "2022-01-28",
            excerpt_zh: "2022年江蘇豐縣一名婦女被鐵鏈鎖頸、生育八孩的影片震驚全國，揭開長期被遮蔽的拐賣黑幕與制度性失職。",
            excerpt_en: "In 2022, a video of a woman chained by the neck in Feng County, Jiangsu—mother of eight—shook the nation, exposing decades of hidden trafficking and systemic neglect.",
            url: "posts/feng-county-chained-woman.html"
        },
        {
            title_zh: "新疆再教育營：21世紀的種族滅絕",
            title_en: "Xinjiang Re-education Camps: A 21st-Century Genocide",
            date: "2017-04-01",
            excerpt_zh: "百萬維吾爾人被秘密關押、強制勞動、強制絕育。多國政府與聯合國報告認定，這可能構成反人類罪甚至種族滅絕。",
            excerpt_en: "Over a million Uyghurs have been secretly detained, forced into labor, and forcibly sterilized. Governments and a UN report conclude this may amount to crimes against humanity, even genocide.",
            url: "posts/xinjiang-camps.html"
        },
        {
            title_zh: "劉曉波與《零八憲章》：未死的良知",
            title_en: "Liu Xiaobo and Charter 08: A Conscience That Refused to Die",
            date: "2017-07-13",
            excerpt_zh: "諾貝爾和平獎得主劉曉波因起草《零八憲章》被判11年重刑，最終病逝獄中——他留下的「我沒有敵人」至今迴盪。",
            excerpt_en: "Nobel Peace laureate Liu Xiaobo was sentenced to 11 years for co-authoring Charter 08 and died in custody. His final words, 'I have no enemies,' still resonate today.",
            url: "posts/liu-xiaobo.html"
        },
        {
            title_zh: "達賴喇嘛流亡與西藏抗暴",
            title_en: "The Dalai Lama in Exile and the Tibetan Uprising",
            date: "1959-03-10",
            excerpt_zh: "1959年拉薩抗暴遭血腥鎮壓，年輕的達賴喇嘛流亡印度，開啟逾六十年的西藏苦難史與精神抵抗。",
            excerpt_en: "The 1959 Lhasa Uprising was crushed in blood, forcing the young Dalai Lama into exile in India and beginning over six decades of Tibetan suffering and spiritual resistance.",
            url: "posts/dalai-lama-exile.html"
        },
        {
            title_zh: "香港國安法與自由的淪陷",
            title_en: "The Hong Kong National Security Law and the Fall of Freedom",
            date: "2020-06-30",
            excerpt_zh: "2020年6月30日，《港區國安法》深夜強推上路，東方之珠的法治、新聞自由與公民社會走向終結，「一國兩制」名存實亡。",
            excerpt_en: "On June 30, 2020, Beijing forced the National Security Law upon Hong Kong, ending the rule of law, press freedom, and civil society—and effectively killing 'One Country, Two Systems'.",
            url: "posts/hong-kong-nsl.html"
        },
        {
            title_zh: "上海封城：清零政策下的人道災難",
            title_en: "Shanghai Lockdown: A Humanitarian Disaster Under Zero-COVID",
            date: "2022-04-01",
            excerpt_zh: "2022年春，兩千五百萬上海市民被強制封控兩個多月，飢餓、次生死亡、暴力執法與被消音的反抗者，揭示了清零政策的真相。",
            excerpt_en: "In spring 2022, 25 million Shanghai residents were locked down for over two months. Starvation, secondary deaths, violent enforcement and silenced resistance revealed the true face of Zero-COVID.",
            url: "posts/shanghai-lockdown.html"
        },
        {
            title_zh: "李文亮醫生：被消音的吹哨人",
            title_en: "Dr. Li Wenliang: The Whistleblower They Silenced",
            date: "2020-02-07",
            excerpt_zh: "率先示警新冠病毒的眼科醫師李文亮被警方訓誡為「造謠者」，最終感染殉職，成為中國言論自由的悲劇象徵。",
            excerpt_en: "Ophthalmologist Li Wenliang was reprimanded by police as a 'rumormonger' for first warning of COVID-19. He died after contracting the virus, becoming a tragic symbol of suppressed speech in China.",
            url: "posts/li-wenliang.html"
        },
        {
            title_zh: "白紙運動：對抗清零政策的吶喊",
            title_en: "White Paper Movement: The Outcry Against Zero-COVID",
            date: "2022-11-26",
            excerpt_zh: "2022年底，中國各地爆發了大規模抗議活動，民眾手舉白紙，抗議嚴苛的封控政策，並喊出了要求自由的口號。",
            excerpt_en: "In late 2022, mass protests erupted across China. People held up blank sheets of paper to protest harsh lockdown policies and shouted slogans demanding freedom.",
            url: "posts/white-paper.html"
        },
        {
            title_zh: "四通橋勇士彭載舟",
            title_en: "Peng Zaizhou: The Lone Protester at Sitong Bridge",
            date: "2022-10-13",
            excerpt_zh: "在中共二十大前夕，彭載舟在北京四通橋掛起橫幅，公開反對習近平獨裁，呼籲罷課罷工罷免獨裁國賊。",
            excerpt_en: "On the eve of the 20th Party Congress, Peng Zaizhou hung banners at Sitong Bridge in Beijing, publicly opposing Xi Jinping's dictatorship and calling for strikes to remove the dictator.",
            url: "posts/peng-zaizhou.html"
        },
        {
            title_zh: "公民記者張展：武漢疫情的真相記錄者",
            title_en: "Citizen Journalist Zhang Zhan: Truth Teller of Wuhan",
            date: "2020-12-28",
            excerpt_zh: "張展因親赴武漢報導COVID-19疫情真相，揭露政府掩蓋的事實，被以'尋釁滋事罪'判處四年有期徒刑。",
            excerpt_en: "Zhang Zhan was sentenced to four years in prison for 'picking quarrels and provoking trouble' after traveling to Wuhan to report the truth about the COVID-19 outbreak.",
            url: "posts/zhang-zhan.html"
        },
        {
            title_zh: "709維權律師大抓捕",
            title_en: "709 Crackdown on Human Rights Lawyers",
            date: "2015-07-09",
            excerpt_zh: "自2015年7月9日起，中共在全國範圍內大規模抓捕、傳喚、刑事拘留維權律師和人權捍衛者，涉及人數超過300人。",
            excerpt_en: "Starting July 9, 2015, the CCP launched a nationwide crackdown, arresting, summoning, and detaining over 300 human rights lawyers and defenders.",
            url: "posts/709-crackdown.html"
        },
        {
            title_zh: "2024年度中國人權狀況報告",
            title_en: "2024 Annual Report on Human Rights in China",
            date: "2025-01-15",
            excerpt_zh: "本報告詳細記錄了過去一年中，中國在言論自由、網絡審查以及少數民族權益方面的倒退...",
            excerpt_en: "This report details the regression in freedom of speech, internet censorship, and minority rights in China over the past year...",
            url: "posts/2024-report.html"
        },
        {
            title_zh: "數字監控與隱私權的終結",
            title_en: "Digital Surveillance and the End of Privacy",
            date: "2024-12-10",
            excerpt_zh: "隨著面部識別和社會信用體系的全面推廣，普通公民的隱私空間正在被極度壓縮...",
            excerpt_en: "With the comprehensive promotion of facial recognition and the social credit system, the privacy of ordinary citizens is being severely compressed...",
            url: "posts/digital-surveillance.html"
        }
    ];

    if (reportsGrid) {
        reports.sort((a, b) => new Date(b.date) - new Date(a.date));
        reports.forEach(report => {
            const card = document.createElement('div');
            card.className = 'report-card';
            card.innerHTML = `
                <div class="report-content">
                    <span class="report-date">${report.date}</span>
                    <h4 class="report-title">
                        <span class="lang-zh">${report.title_zh}</span>
                        <span class="lang-en">${report.title_en}</span>
                    </h4>
                    <p class="report-excerpt">
                        <span class="lang-zh">${report.excerpt_zh}</span>
                        <span class="lang-en">${report.excerpt_en}</span>
                    </p>
                    <a href="${report.url}" class="read-more">
                        <span class="lang-zh">閱讀全文 &rarr;</span>
                        <span class="lang-en">Read More &rarr;</span>
                    </a>
                </div>
            `;
            reportsGrid.appendChild(card);
        });
    }

    // Scroll Animation (Intersection Observer)
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.about-card, .report-card, .timeline-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease-out';
        observer.observe(el);
    });
});

