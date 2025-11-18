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
            url: "#"
        },
        {
            title_zh: "數字監控與隱私權的終結",
            title_en: "Digital Surveillance and the End of Privacy",
            date: "2024-12-10",
            excerpt_zh: "隨著面部識別和社會信用體系的全面推廣，普通公民的隱私空間正在被極度壓縮...",
            excerpt_en: "With the comprehensive promotion of facial recognition and the social credit system, the privacy of ordinary citizens is being severely compressed...",
            url: "#"
        }
    ];

    if (reportsGrid) {
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

