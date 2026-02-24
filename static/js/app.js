/* ── TechTips — Education Innovation Hub ──────────────────────────── */

// ── School Values ───────────────────────────────────────────────────
// Each article gets auto-tagged with school values based on keyword matching.

const SCHOOL_VALUES = {
    courage: {
        label: 'Courage',
        description: 'We face challenges directly. We are bold in our ambitions and pursue excellence.',
        keywords: ['bold', 'brave', 'challenge', 'ambitious', 'ambition', 'excellence', 'risk', 'resilience', 'resilient', 'fearless', 'overcome', 'determination', 'grit', 'perseverance', 'daring', 'confident', 'confidence', 'stand up', 'courageous', 'adversity', 'pioneering', 'transformative', 'disrupt', 'radical'],
    },
    curiosity: {
        label: 'Curiosity',
        description: 'We nurture a love of learning by asking questions and exploring new ideas.',
        keywords: ['curiosity', 'curious', 'inquiry', 'enquiry', 'question', 'explore', 'discover', 'discovery', 'investigate', 'research', 'wonder', 'experiment', 'innovation', 'innovative', 'creative', 'creativity', 'imagination', 'intellectual', 'learning', 'interdisciplinary', 'critical thinking', 'problem-solving', 'stem', 'science'],
    },
    integrity: {
        label: 'Integrity',
        description: 'We do what is right, even if it is not easy. We take responsibility for our actions.',
        keywords: ['integrity', 'honest', 'honesty', 'ethical', 'ethics', 'responsible', 'responsibility', 'accountable', 'accountability', 'transparent', 'transparency', 'trust', 'moral', 'principled', 'fairness', 'fair', 'truth', 'authentic', 'genuine', 'standards', 'safeguarding', 'governance'],
    },
    kindness: {
        label: 'Kindness',
        description: 'We are an empathetic, compassionate community where everyone feels valued and included.',
        keywords: ['kind', 'kindness', 'empathy', 'empathetic', 'compassion', 'compassionate', 'caring', 'support', 'supporting', 'wellbeing', 'well-being', 'mental health', 'pastoral', 'nurture', 'nurturing', 'inclusive', 'inclusion', 'belonging', 'community', 'safe space', 'welfare', 'emotional'],
    },
    respect: {
        label: 'Respect',
        description: 'We respect each other and the world around us, upholding the dignity of every individual.',
        keywords: ['respect', 'dignity', 'diverse', 'diversity', 'equity', 'equality', 'listen', 'listening', 'open-minded', 'tolerance', 'tolerant', 'culture', 'cultural', 'multicultural', 'global', 'international', 'sustainability', 'sustainable', 'environment', 'environmental', 'human rights', 'democracy'],
    },
    service: {
        label: 'Service',
        description: 'We seek to make a positive difference through meaningful contributions and leadership.',
        keywords: ['service', 'serve', 'volunteer', 'volunteering', 'community service', 'leadership', 'leader', 'contribute', 'contribution', 'philanthropy', 'charity', 'social impact', 'civic', 'citizenship', 'mentor', 'mentoring', 'outreach', 'greater good', 'give back', 'making a difference', 'enterprise'],
    },
};

// ── Haileybury 2030 Academic Ambitions ──────────────────────────────
// Articles matching these themes are especially relevant.

const ACADEMIC_AMBITIONS = {
    curriculum: {
        label: 'Curriculum & Independence',
        keywords: ['curriculum', 'interdisciplinary', 'cross-curricular', 'broad curriculum', 'independent learning', 'real-world', 'applied learning', 'passion', 'intellectual', 'theoretical', '21st century skills', 'future skills'],
    },
    pedagogy: {
        label: 'Pedagogical Excellence',
        keywords: ['pedagogy', 'pedagogical', 'teaching quality', 'teaching excellence', 'instruction', 'instructional', 'evidence-based teaching', 'effective teaching', 'teacher development', 'cpd', 'professional development', 'coaching'],
    },
    technology: {
        label: 'Technology & Digital',
        keywords: ['edtech', 'educational technology', 'digital', 'technology in education', 'ai in education', 'artificial intelligence', 'digital literacy', 'blended learning', 'online learning', 'digital resources', 'balanced technology'],
    },
    leadership_enterprise: {
        label: 'Leadership & Enterprise',
        keywords: ['leadership', 'enterprise', 'entrepreneurship', 'employability', 'career', 'careers', 'industry', 'partnership', 'work experience', 'goal-setting', 'ambition', 'aspiration', 'competencies'],
    },
    executive_function: {
        label: 'Learning Habits',
        keywords: ['executive function', 'metacognition', 'self-regulation', 'study skills', 'learning habits', 'revision', 'organisation', 'focus', 'motivation', 'growth mindset', 'mindset', 'resilience', 'independent learner'],
    },
    assessment: {
        label: 'Assessment & Reporting',
        keywords: ['assessment', 'reporting', 'grading', 'marking', 'feedback', 'formative', 'summative', 'exam', 'examination', 'gcse', 'a-level', 'ib', 'qualification', 'attainment'],
    },
    university: {
        label: 'University & Futures',
        keywords: ['university', 'higher education', 'oxbridge', 'russell group', 'ucas', 'personal statement', 'career pathway', 'future', 'futures', 'global citizenship', 'diversity', 'community service'],
    },
};


// ── State ───────────────────────────────────────────────────────────
let currentSection = 'home';
let feedArticles = [];
let allResources = [];
let currentFeedFilter = 'all';
let activeValueFilter = null;


// ── Navigation ──────────────────────────────────────────────────────
function showSection(section) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    const sectionEl = document.getElementById(`section-${section}`);
    const navEl = document.querySelector(`[data-section="${section}"]`);
    if (sectionEl) sectionEl.classList.add('active');
    if (navEl) navEl.classList.add('active');
    currentSection = section;

    // Close mobile nav on navigation
    document.getElementById('sidebar').classList.remove('open');

    // Load data for sections on first visit
    if (section === 'home') loadHome();
    if (section === 'articles') loadFeed();
    if (section === 'resources') loadResources();
    if (section === 'reading-list') loadReadingList();
    if (section === 'notes') loadNotes();
    if (section === 'sources') loadSources();
}

function toggleMobileNav() {
    document.getElementById('sidebar').classList.toggle('open');
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => showSection(item.dataset.section));
    });
    loadHome();
});


// ── Values Tagging Engine ───────────────────────────────────────────
function tagArticleWithValues(article) {
    const text = `${article.title} ${article.summary || ''}`.toLowerCase();
    const values = [];

    for (const [key, value] of Object.entries(SCHOOL_VALUES)) {
        for (const keyword of value.keywords) {
            if (text.includes(keyword)) {
                values.push(key);
                break;
            }
        }
    }

    return values;
}

function tagArticleWithAmbitions(article) {
    const text = `${article.title} ${article.summary || ''}`.toLowerCase();
    const ambitions = [];

    for (const [key, ambition] of Object.entries(ACADEMIC_AMBITIONS)) {
        for (const keyword of ambition.keywords) {
            if (text.includes(keyword)) {
                ambitions.push(key);
                break;
            }
        }
    }

    return ambitions;
}

function renderValueTags(values) {
    if (!values || values.length === 0) return '';
    return `<div class="value-tags">
        ${values.map(v => `<span class="value-tag ${v}">${SCHOOL_VALUES[v]?.label || v}</span>`).join('')}
    </div>`;
}


// ── Home Page ───────────────────────────────────────────────────────
let homeLoaded = false;

async function loadHome() {
    if (!homeLoaded) {
        loadFeaturedResources();
        loadHomeArticles();
        homeLoaded = true;
    }
}

async function loadFeaturedResources() {
    const container = document.getElementById('featured-resources');
    try {
        const res = await fetch('/api/resources/featured');
        const resources = await res.json();
        if (resources.length === 0) {
            container.innerHTML = '<p style="color:var(--text-muted);">No resources yet.</p>';
            return;
        }
        container.innerHTML = resources.map(r => `
            <div class="featured-card">
                <h4><a href="${escapeHtml(r.url)}" target="_blank" rel="noopener">${escapeHtml(r.title)}</a></h4>
                <p>${escapeHtml(r.description)}</p>
                <div class="resource-meta">
                    <span class="tag">${getCategoryLabel(r.category)}</span>
                </div>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p style="color:var(--text-muted);">Could not load resources.</p>`;
    }
}

async function loadHomeArticles() {
    const container = document.getElementById('home-articles');
    container.innerHTML = `<div class="loading"><div class="spinner"></div>Fetching latest articles...</div>`;

    try {
        const res = await fetch('/api/feed');
        feedArticles = await res.json();

        // Tag all articles with values
        feedArticles.forEach(a => {
            a._values = tagArticleWithValues(a);
            a._ambitions = tagArticleWithAmbitions(a);
        });

        // Show top 6 on home
        const preview = feedArticles.slice(0, 6);
        if (preview.length === 0) {
            container.innerHTML = `<div class="empty-state"><h3>No articles yet</h3><p>Check your feed sources or try refreshing.</p></div>`;
            return;
        }
        container.innerHTML = preview.map(a => renderArticleCard(a, true)).join('');
    } catch (err) {
        container.innerHTML = `<div class="empty-state"><h3>Could not load feed</h3><p>${escapeHtml(err.message)}</p></div>`;
    }
}


// ── Articles / Feed ─────────────────────────────────────────────────
async function loadFeed() {
    const container = document.getElementById('feed-articles');

    if (feedArticles.length > 0) {
        renderFeed();
        return;
    }

    container.innerHTML = `<div class="loading"><div class="spinner"></div>Fetching latest articles from education feeds...</div>`;

    try {
        const res = await fetch('/api/feed');
        feedArticles = await res.json();
        feedArticles.forEach(a => {
            a._values = tagArticleWithValues(a);
            a._ambitions = tagArticleWithAmbitions(a);
        });
        renderFeed();
    } catch (err) {
        container.innerHTML = `<div class="empty-state"><div class="icon">!</div><h3>Could not load feed</h3><p>${escapeHtml(err.message)}</p></div>`;
    }
}

function renderFeed() {
    const container = document.getElementById('feed-articles');
    let filtered = feedArticles;

    if (currentFeedFilter !== 'all') {
        filtered = filtered.filter(a => a.category === currentFeedFilter);
    }

    if (activeValueFilter) {
        filtered = filtered.filter(a => a._values && a._values.includes(activeValueFilter));
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>No articles match</h3>
                <p>Try a different filter or check your feed sources.</p>
            </div>`;
        return;
    }

    container.innerHTML = filtered.map(a => renderArticleCard(a, false)).join('');
}

function renderArticleCard(article, compact) {
    const valueTags = renderValueTags(article._values);
    const summary = compact ? truncate(article.summary || '', 120) : truncate(article.summary || '', 200);

    return `
        <div class="article-card">
            <h3><a href="${escapeHtml(article.url)}" target="_blank" rel="noopener">${escapeHtml(article.title)}</a></h3>
            <div class="article-meta">
                <span class="source-badge">${escapeHtml(article.source_name || article.source)}</span>
                ${article.category ? `<span class="category-badge">${escapeHtml(article.category)}</span>` : ''}
                ${article.published ? `<span>${escapeHtml(article.published)}</span>` : ''}
            </div>
            <div class="article-summary">${summary}</div>
            ${valueTags}
            ${!compact ? `
                <div class="article-actions">
                    <button class="btn btn-sm btn-primary" onclick='saveArticle(${JSON.stringify(article).replace(/'/g, "&#39;")})'>
                        Save to Reading List
                    </button>
                </div>
            ` : ''}
        </div>
    `;
}

function filterFeed(category) {
    currentFeedFilter = category;
    document.querySelectorAll('.feed-filters .filter-chip').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    renderFeed();
}

function filterByValue(value) {
    if (activeValueFilter === value) {
        activeValueFilter = null;
    } else {
        activeValueFilter = value;
    }

    // Update chip states
    document.querySelectorAll('.value-chip').forEach(c => {
        if (activeValueFilter === null) {
            c.classList.remove('active', 'inactive');
        } else if (c.dataset.value === activeValueFilter) {
            c.classList.add('active');
            c.classList.remove('inactive');
        } else {
            c.classList.add('inactive');
            c.classList.remove('active');
        }
    });

    renderFeed();
}


// ── Surprise Me ─────────────────────────────────────────────────────
function surpriseMe() {
    if (feedArticles.length === 0) {
        alert('Articles are still loading — try again in a moment.');
        return;
    }

    const idx = Math.floor(Math.random() * feedArticles.length);
    const article = feedArticles[idx];
    const valueTags = renderValueTags(article._values);

    const container = document.getElementById('surprise-content');
    container.innerHTML = `
        <div class="surprise-article">
            <h3><a href="${escapeHtml(article.url)}" target="_blank" rel="noopener">${escapeHtml(article.title)}</a></h3>
            <div class="article-meta">
                <span class="source-badge">${escapeHtml(article.source_name || article.source)}</span>
                ${article.category ? `<span class="category-badge">${escapeHtml(article.category)}</span>` : ''}
                ${article.published ? `<span>${escapeHtml(article.published)}</span>` : ''}
            </div>
            <div class="article-summary">${escapeHtml(article.summary || '')}</div>
            ${valueTags}
            <div class="article-actions" style="margin-top:16px;">
                <button class="btn btn-sm btn-primary" onclick='saveArticle(${JSON.stringify(article).replace(/'/g, "&#39;")})'>
                    Save to Reading List
                </button>
                <a href="${escapeHtml(article.url)}" target="_blank" rel="noopener" class="btn btn-sm btn-secondary">
                    Read Article
                </a>
            </div>
        </div>
    `;

    document.getElementById('surprise-modal').classList.add('active');
}

function closeSurpriseModal() {
    document.getElementById('surprise-modal').classList.remove('active');
}


// ── Resources ───────────────────────────────────────────────────────
let resourcesLoaded = false;

async function loadResources() {
    if (resourcesLoaded && allResources.length > 0) {
        renderResources();
        return;
    }

    const container = document.getElementById('resources-list');
    container.innerHTML = `<div class="loading"><div class="spinner"></div>Loading resources...</div>`;

    try {
        const res = await fetch('/api/resources');
        allResources = await res.json();
        resourcesLoaded = true;
        renderResources();
    } catch (err) {
        container.innerHTML = `<p style="color:var(--text-muted);">Could not load resources.</p>`;
    }
}

function renderResources(filterCategory) {
    const container = document.getElementById('resources-list');
    let resources = allResources;

    if (filterCategory && filterCategory !== 'all') {
        resources = resources.filter(r => r.category === filterCategory);
    }

    if (resources.length === 0) {
        container.innerHTML = `<div class="empty-state"><h3>No resources found</h3></div>`;
        return;
    }

    // Group by category
    const groups = {};
    resources.forEach(r => {
        if (!groups[r.category]) groups[r.category] = [];
        groups[r.category].push(r);
    });

    let html = '';
    for (const [cat, items] of Object.entries(groups)) {
        html += `
            <div class="resource-category-group">
                <h3 class="resource-category-title">${getCategoryLabel(cat)}</h3>
                <div class="resource-grid">
                    ${items.map(r => `
                        <div class="resource-card">
                            <h4><a href="${escapeHtml(r.url)}" target="_blank" rel="noopener">${escapeHtml(r.title)}</a></h4>
                            <p>${escapeHtml(r.description)}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

function filterResources(category) {
    document.querySelectorAll('.resource-filters .filter-chip').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    renderResources(category);
}

function showResourceCategory(category) {
    showSection('resources');
    // Activate the correct filter chip
    document.querySelectorAll('.resource-filters .filter-chip').forEach(c => {
        c.classList.remove('active');
        if (c.dataset.cat === category) c.classList.add('active');
    });
    renderResources(category);
}


// ── Reading List (Saved Articles) ───────────────────────────────────
async function loadReadingList() {
    const container = document.getElementById('reading-list-content');
    try {
        const res = await fetch('/api/articles');
        const articles = await res.json();
        if (articles.length === 0) {
            container.innerHTML = `<div class="empty-state"><div class="icon">&#9776;</div><h3>Reading list is empty</h3><p>Save articles from the feed to read later.</p></div>`;
            return;
        }
        container.innerHTML = articles.map(a => `
            <div class="article-card">
                <h3><a href="${escapeHtml(a.url)}" target="_blank">${escapeHtml(a.title)}</a></h3>
                <div class="article-meta">
                    <span class="source-badge">${escapeHtml(a.source || '')}</span>
                    <span>${escapeHtml(a.created_at || '')}</span>
                </div>
                <div class="article-summary">${escapeHtml(a.summary || '')}</div>
                ${a.tags ? `<div style="margin-top:6px;">${a.tags.split(',').map(t => `<span class="tag">${escapeHtml(t.trim())}</span>`).join('')}</div>` : ''}
                <div class="article-actions">
                    <button class="btn btn-sm btn-danger" onclick="deleteArticle(${a.id})">Remove</button>
                </div>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p>Error loading reading list: ${escapeHtml(err.message)}</p>`;
    }
}

async function searchReadingList() {
    const query = document.getElementById('reading-search').value.trim();
    if (!query) { loadReadingList(); return; }

    const container = document.getElementById('reading-list-content');
    try {
        const res = await fetch(`/api/articles/search?q=${encodeURIComponent(query)}`);
        const results = await res.json();
        if (results.length === 0) {
            container.innerHTML = `<div class="empty-state"><h3>No results</h3><p>No matches for "${escapeHtml(query)}"</p></div>`;
            return;
        }
        container.innerHTML = results.map(a => `
            <div class="article-card">
                <h3><a href="${escapeHtml(a.url)}" target="_blank">${escapeHtml(a.title)}</a></h3>
                <div class="article-summary">${escapeHtml(a.summary || '')}</div>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p>Error: ${escapeHtml(err.message)}</p>`;
    }
}

async function saveArticle(article) {
    try {
        await fetch('/api/articles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: article.title,
                url: article.url,
                source: article.source_name || article.source,
                summary: article.summary || '',
                tags: (article._values || []).concat(article.category ? [article.category] : []).join(', '),
            }),
        });
        alert('Saved to your reading list!');
    } catch (err) {
        alert('Error saving article: ' + err.message);
    }
}

async function deleteArticle(id) {
    if (!confirm('Remove this article from your reading list?')) return;
    await fetch(`/api/articles/${id}`, { method: 'DELETE' });
    loadReadingList();
}


// ── Notes ───────────────────────────────────────────────────────────
async function loadNotes() {
    const container = document.getElementById('notes-content');
    try {
        const res = await fetch('/api/notes');
        const notes = await res.json();
        if (notes.length === 0) {
            container.innerHTML = `<div class="empty-state"><div class="icon">&#9998;</div><h3>No notes yet</h3><p>Create your first note to start building your knowledge base.</p></div>`;
            return;
        }
        container.innerHTML = notes.map(n => `
            <div class="note-card">
                <h3>${escapeHtml(n.title)}</h3>
                <div class="note-content">${escapeHtml(truncate(n.content, 300))}</div>
                <div class="note-meta">
                    ${n.tags ? n.tags.split(',').map(t => `<span class="tag">${escapeHtml(t.trim())}</span>`).join('') : ''}
                    <span>${escapeHtml(n.created_at || '')}</span>
                </div>
                <div class="article-actions" style="margin-top:8px;">
                    <button class="btn btn-sm btn-danger" onclick="deleteNote(${n.id})">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p>Error loading notes: ${escapeHtml(err.message)}</p>`;
    }
}

async function searchNotes() {
    const query = document.getElementById('notes-search').value.trim();
    if (!query) { loadNotes(); return; }

    const container = document.getElementById('notes-content');
    try {
        const res = await fetch(`/api/notes/search?q=${encodeURIComponent(query)}`);
        const results = await res.json();
        if (results.length === 0) {
            container.innerHTML = `<div class="empty-state"><h3>No results</h3><p>No matches for "${escapeHtml(query)}"</p></div>`;
            return;
        }
        container.innerHTML = results.map(n => `
            <div class="note-card"><h3>${escapeHtml(n.title)}</h3><div class="note-content">${escapeHtml(truncate(n.content, 300))}</div></div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p>Error: ${escapeHtml(err.message)}</p>`;
    }
}

function showCreateNote() {
    document.getElementById('note-modal').classList.add('active');
}

function closeNoteModal() {
    document.getElementById('note-modal').classList.remove('active');
}

async function createNote() {
    const title = document.getElementById('note-title').value.trim();
    const content = document.getElementById('note-content').value.trim();
    const tags = document.getElementById('note-tags').value.trim();

    if (!title || !content) { alert('Title and content are required'); return; }

    try {
        await fetch('/api/notes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content, tags }),
        });
        closeNoteModal();
        document.getElementById('note-title').value = '';
        document.getElementById('note-content').value = '';
        document.getElementById('note-tags').value = '';
        showSection('notes');
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

async function deleteNote(id) {
    if (!confirm('Delete this note?')) return;
    await fetch(`/api/notes/${id}`, { method: 'DELETE' });
    loadNotes();
}


// ── Feed Sources ────────────────────────────────────────────────────
async function loadSources() {
    const container = document.getElementById('sources-list');
    try {
        const res = await fetch('/api/feed/sources');
        const sources = await res.json();
        if (sources.length === 0) {
            container.innerHTML = '<p style="color:var(--text-muted);">No feed sources configured.</p>';
            return;
        }
        container.innerHTML = sources.map(s => `
            <div class="source-item">
                <div class="source-info">
                    <strong>${escapeHtml(s.name)}</strong>
                    <span class="tag">${escapeHtml(s.category || 'general')}</span>
                    <div class="source-url">${escapeHtml(s.url)}</div>
                </div>
                <button class="btn btn-sm btn-danger" onclick="removeSource(${s.id})">Remove</button>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p>Error: ${escapeHtml(err.message)}</p>`;
    }
}

async function addSource() {
    const name = document.getElementById('new-source-name').value.trim();
    const url = document.getElementById('new-source-url').value.trim();
    const category = document.getElementById('new-source-category').value;

    if (!name || !url) { alert('Name and URL are required'); return; }

    try {
        await fetch('/api/feed/sources', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, url, category }),
        });
        document.getElementById('new-source-name').value = '';
        document.getElementById('new-source-url').value = '';
        loadSources();
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

async function removeSource(id) {
    if (!confirm('Remove this feed source?')) return;
    await fetch(`/api/feed/sources/${id}`, { method: 'DELETE' });
    loadSources();
}


// ── Utilities ───────────────────────────────────────────────────────
function truncate(text, max) {
    if (!text) return '';
    const stripped = text.replace(/<[^>]*>/g, '');
    return stripped.length > max ? stripped.substring(0, max) + '...' : stripped;
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function getCategoryLabel(cat) {
    const labels = {
        ai: 'AI in Education',
        pbl: 'Project-Based Learning',
        assessment: 'Assessment Innovation',
        digital: 'Digital & Computing',
        enterprise: 'Enterprise & Careers',
        research: 'Research & Evidence',
        inclusion: 'Inclusive Education',
        education: 'Education',
        edtech: 'EdTech',
        policy: 'Policy',
        pedagogy: 'Pedagogy',
        general: 'General',
    };
    return labels[cat] || cat;
}
