/* ── TechTips Education Knowledge Base — Frontend ────────────── */

// ── State ───────────────────────────────────────────────────────
let currentSection = 'perspectives';
let currentPerspective = null;
let feedArticles = [];
let currentFeedFilter = 'all';
let currentLibTab = 'articles';

// ── Navigation ──────────────────────────────────────────────────
function showSection(section) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    document.getElementById(`section-${section}`).classList.add('active');
    document.querySelector(`[data-section="${section}"]`).classList.add('active');
    currentSection = section;

    if (section === 'feed') loadFeed();
    if (section === 'library') loadLibrary();
    if (section === 'history') loadHistory();
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => showSection(item.dataset.section));
    });
    showSection('perspectives');
});

// ── Perspectives Engine ─────────────────────────────────────────
async function askQuestion() {
    const textarea = document.getElementById('question-input');
    const question = textarea.value.trim();
    if (!question) return;

    const resultsDiv = document.getElementById('perspectives-results');
    resultsDiv.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            Generating three perspectives — this takes a moment...
        </div>`;

    document.getElementById('ask-btn').disabled = true;

    try {
        const res = await fetch('/api/perspectives', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || 'Failed to generate perspectives');
        }

        const data = await res.json();
        currentPerspective = data;
        renderPerspectives(data);
    } catch (err) {
        resultsDiv.innerHTML = `
            <div class="card" style="border-left: 4px solid var(--danger);">
                <p><strong>Error:</strong> ${err.message}</p>
                <p style="font-size:0.85rem; color:var(--text-muted); margin-top:8px;">
                    Make sure your ANTHROPIC_API_KEY is set in the .env file.</p>
            </div>`;
    } finally {
        document.getElementById('ask-btn').disabled = false;
    }
}

function renderPerspectives(data) {
    const resultsDiv = document.getElementById('perspectives-results');

    const cautious = data.cautious || {};
    const radical = data.radical || {};
    const pragmatic = data.pragmatic || {};
    const verdict = data.verdict || {};

    resultsDiv.innerHTML = `
        <div class="perspective-grid">
            ${renderPerspectiveCard(cautious, 'cautious')}
            ${renderPerspectiveCard(radical, 'radical')}
            ${renderPerspectiveCard(pragmatic, 'pragmatic')}
        </div>

        <div class="debate-section">
            <h3>The Debate</h3>
            <p>${data.debate || ''}</p>
        </div>

        <div class="verdict-section">
            <h3>Verdict</h3>
            <span class="strongest ${verdict.strongest || ''}">${getVerdictLabel(verdict.strongest)}</span>
            <p>${verdict.explanation || ''}</p>
        </div>

        <div class="followup-area">
            <h3 style="font-size:0.95rem; margin-bottom:8px;">Ask a follow-up</h3>
            <textarea id="followup-input" placeholder="Push the debate further — challenge a perspective, ask for more detail, or explore a related angle..."></textarea>
            <button class="btn btn-accent" onclick="askFollowup()">Continue the Debate</button>
            <div id="followup-results"></div>
        </div>
    `;
}

function renderPerspectiveCard(p, type) {
    const supportList = (p.supporting_evidence || []).map(e => `<li>${e}</li>`).join('');
    const contradictList = (p.contradicting_evidence || []).map(e => `<li>${e}</li>`).join('');

    return `
        <div class="perspective-card ${type}">
            <h3>${p.name || type}</h3>
            <div class="stance">${p.stance || ''}</div>
            <div class="argument">${p.argument || ''}</div>
            <div class="evidence-section">
                <h4>Supporting Evidence</h4>
                <ul>${supportList}</ul>
                <h4>Contradicting Evidence</h4>
                <ul>${contradictList}</ul>
            </div>
        </div>
    `;
}

function getVerdictLabel(strongest) {
    const labels = {
        cautious: 'The Guardian — Strongest',
        radical: 'The Radical — Strongest',
        pragmatic: 'The Pragmatist — Strongest',
    };
    return labels[strongest] || 'Analysis';
}

async function askFollowup() {
    const input = document.getElementById('followup-input');
    const followup = input.value.trim();
    if (!followup || !currentPerspective) return;

    const resultsDiv = document.getElementById('followup-results');
    resultsDiv.innerHTML = `<div class="loading"><div class="spinner"></div>Continuing the debate...</div>`;

    try {
        const res = await fetch('/api/perspectives/followup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: currentPerspective.question,
                original: currentPerspective,
                followup,
            }),
        });

        const data = await res.json();
        resultsDiv.innerHTML = `<div class="followup-response">${data.response}</div>`;
        input.value = '';
    } catch (err) {
        resultsDiv.innerHTML = `<div class="card"><p>Error: ${err.message}</p></div>`;
    }
}

// ── Newsfeed ────────────────────────────────────────────────────
async function loadFeed() {
    const container = document.getElementById('feed-articles');
    container.innerHTML = `<div class="loading"><div class="spinner"></div>Fetching latest articles from education feeds...</div>`;

    try {
        const res = await fetch('/api/feed');
        feedArticles = await res.json();
        renderFeed();
    } catch (err) {
        container.innerHTML = `<div class="empty-state"><div class="icon">!</div><h3>Could not load feed</h3><p>${err.message}</p></div>`;
    }
}

function renderFeed() {
    const container = document.getElementById('feed-articles');
    let filtered = feedArticles;

    if (currentFeedFilter !== 'all') {
        filtered = feedArticles.filter(a => a.category === currentFeedFilter);
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">📡</div>
                <h3>No articles yet</h3>
                <p>Check your feed sources or try a different filter.</p>
            </div>`;
        return;
    }

    container.innerHTML = filtered.map(article => `
        <div class="article-card">
            <h3><a href="${article.url}" target="_blank" rel="noopener">${article.title}</a></h3>
            <div class="article-meta">
                <span>${article.source_name || article.source}</span>
                <span>${article.category || ''}</span>
                ${article.published ? `<span>${article.published}</span>` : ''}
            </div>
            <div class="article-summary">${truncate(article.summary || '', 200)}</div>
            <div class="article-actions">
                <button class="btn btn-sm btn-secondary" onclick="saveArticle(${JSON.stringify(article).replace(/"/g, '&quot;')})">
                    Save to Library
                </button>
                <button class="btn btn-sm btn-secondary" onclick="summariseArticle('${escapeJs(article.title)}', '${escapeJs(article.summary || '')}')">
                    AI Summary
                </button>
            </div>
        </div>
    `).join('');
}

function filterFeed(category) {
    currentFeedFilter = category;
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    renderFeed();
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
                tags: article.category || '',
            }),
        });
        alert('Article saved to library!');
    } catch (err) {
        alert('Error saving article: ' + err.message);
    }
}

async function summariseArticle(title, content) {
    const container = document.getElementById('summary-modal-content');
    const overlay = document.getElementById('summary-modal');
    overlay.classList.add('active');
    container.innerHTML = `<div class="loading"><div class="spinner"></div>Generating AI summary...</div>`;

    try {
        const res = await fetch('/api/feed/summarise', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content }),
        });
        const data = await res.json();

        const tags = (data.tags || []).map(t => `<span class="tag">${t}</span>`).join(' ');
        container.innerHTML = `
            <h3 style="font-size:0.95rem; margin-bottom:8px;">${title}</h3>
            <p style="font-size:0.9rem; line-height:1.6; margin-bottom:12px;">${data.summary}</p>
            <div>${tags}</div>
            <p style="font-size:0.8rem; color:var(--text-muted); margin-top:8px;">
                Relevance score: ${data.relevance_score}/10
            </p>
        `;
    } catch (err) {
        container.innerHTML = `<p>Error: ${err.message}</p>`;
    }
}

function closeSummaryModal() {
    document.getElementById('summary-modal').classList.remove('active');
}

// ── Library ─────────────────────────────────────────────────────
function switchLibTab(tab) {
    currentLibTab = tab;
    document.querySelectorAll('.lib-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    loadLibrary();
}

async function loadLibrary() {
    const container = document.getElementById('library-content');

    if (currentLibTab === 'articles') {
        try {
            const res = await fetch('/api/articles');
            const articles = await res.json();
            if (articles.length === 0) {
                container.innerHTML = `<div class="empty-state"><div class="icon">📚</div><h3>No saved articles</h3><p>Save articles from the newsfeed to see them here.</p></div>`;
                return;
            }
            container.innerHTML = articles.map(a => `
                <div class="article-card">
                    <h3><a href="${a.url}" target="_blank">${a.title}</a></h3>
                    <div class="article-meta">
                        <span>${a.source || ''}</span>
                        <span>${a.created_at || ''}</span>
                    </div>
                    <div class="article-summary">${a.summary || ''}</div>
                    ${a.tags ? `<div style="margin-top:6px;">${a.tags.split(',').map(t => `<span class="tag">${t.trim()}</span>`).join('')}</div>` : ''}
                    <div class="article-actions">
                        <button class="btn btn-sm btn-danger" onclick="deleteArticle(${a.id})">Remove</button>
                    </div>
                </div>
            `).join('');
        } catch (err) {
            container.innerHTML = `<p>Error loading articles: ${err.message}</p>`;
        }
    } else if (currentLibTab === 'notes') {
        try {
            const res = await fetch('/api/notes');
            const notes = await res.json();
            if (notes.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="icon">📝</div>
                        <h3>No notes yet</h3>
                        <p>Create your first note to start building your knowledge base.</p>
                    </div>`;
                return;
            }
            container.innerHTML = notes.map(n => `
                <div class="note-card">
                    <h3>${n.title}</h3>
                    <div class="note-content">${truncate(n.content, 300)}</div>
                    <div class="note-meta">
                        ${n.tags ? n.tags.split(',').map(t => `<span class="tag">${t.trim()}</span>`).join('') : ''}
                        <span>${n.created_at || ''}</span>
                    </div>
                    <div class="article-actions" style="margin-top:8px;">
                        <button class="btn btn-sm btn-danger" onclick="deleteNote(${n.id})">Delete</button>
                    </div>
                </div>
            `).join('');
        } catch (err) {
            container.innerHTML = `<p>Error loading notes: ${err.message}</p>`;
        }
    } else if (currentLibTab === 'collections') {
        try {
            const res = await fetch('/api/collections');
            const collections = await res.json();
            if (collections.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="icon">📁</div>
                        <h3>No collections yet</h3>
                        <p>Organise your articles and notes into themed collections.</p>
                    </div>`;
                return;
            }
            container.innerHTML = collections.map(c => `
                <div class="card">
                    <div class="card-header">
                        <h2>${c.name}</h2>
                        <button class="btn btn-sm btn-danger" onclick="deleteCollection(${c.id})">Delete</button>
                    </div>
                    <p style="font-size:0.88rem; color:var(--text-muted);">${c.description || ''}</p>
                </div>
            `).join('');
        } catch (err) {
            container.innerHTML = `<p>Error loading collections: ${err.message}</p>`;
        }
    }
}

async function searchLibrary() {
    const query = document.getElementById('library-search').value.trim();
    if (!query) { loadLibrary(); return; }

    const container = document.getElementById('library-content');
    const endpoint = currentLibTab === 'notes' ? '/api/notes/search' : '/api/articles/search';

    try {
        const res = await fetch(`${endpoint}?q=${encodeURIComponent(query)}`);
        const results = await res.json();

        if (results.length === 0) {
            container.innerHTML = `<div class="empty-state"><h3>No results</h3><p>No matches found for "${query}"</p></div>`;
            return;
        }

        if (currentLibTab === 'notes') {
            container.innerHTML = results.map(n => `
                <div class="note-card"><h3>${n.title}</h3><div class="note-content">${truncate(n.content, 300)}</div></div>
            `).join('');
        } else {
            container.innerHTML = results.map(a => `
                <div class="article-card"><h3><a href="${a.url}" target="_blank">${a.title}</a></h3><div class="article-summary">${a.summary || ''}</div></div>
            `).join('');
        }
    } catch (err) {
        container.innerHTML = `<p>Error: ${err.message}</p>`;
    }
}

async function deleteArticle(id) {
    if (!confirm('Remove this article?')) return;
    await fetch(`/api/articles/${id}`, { method: 'DELETE' });
    loadLibrary();
}

async function deleteNote(id) {
    if (!confirm('Delete this note?')) return;
    await fetch(`/api/notes/${id}`, { method: 'DELETE' });
    loadLibrary();
}

async function deleteCollection(id) {
    if (!confirm('Delete this collection and all its items?')) return;
    await fetch(`/api/collections/${id}`, { method: 'DELETE' });
    loadLibrary();
}

// ── Create Note Modal ───────────────────────────────────────────
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
        currentLibTab = 'notes';
        showSection('library');
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

// ── Create Collection Modal ─────────────────────────────────────
function showCreateCollection() {
    document.getElementById('collection-modal').classList.add('active');
}

function closeCollectionModal() {
    document.getElementById('collection-modal').classList.remove('active');
}

async function createCollection() {
    const name = document.getElementById('collection-name').value.trim();
    const desc = document.getElementById('collection-desc').value.trim();

    if (!name) { alert('Collection name is required'); return; }

    try {
        await fetch('/api/collections', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description: desc }),
        });
        closeCollectionModal();
        document.getElementById('collection-name').value = '';
        document.getElementById('collection-desc').value = '';
        currentLibTab = 'collections';
        showSection('library');
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

// ── History ─────────────────────────────────────────────────────
async function loadHistory() {
    const container = document.getElementById('history-list');
    try {
        const res = await fetch('/api/perspectives');
        const perspectives = await res.json();

        if (perspectives.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">💬</div>
                    <h3>No debates yet</h3>
                    <p>Ask a question in the Perspectives tab to start your first debate.</p>
                </div>`;
            return;
        }

        container.innerHTML = perspectives.map(p => `
            <div class="history-item" onclick="viewHistoryItem(${p.id}, '${escapeJs(p.question)}')">
                <h4>${p.question}</h4>
                <div class="date">${p.created_at || ''}</div>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p>Error: ${err.message}</p>`;
    }
}

function viewHistoryItem(id, question) {
    document.getElementById('question-input').value = question;
    showSection('perspectives');
}

// ── Utilities ───────────────────────────────────────────────────
function truncate(text, max) {
    if (!text) return '';
    const stripped = text.replace(/<[^>]*>/g, '');
    return stripped.length > max ? stripped.substring(0, max) + '...' : stripped;
}

function escapeJs(str) {
    return (str || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n');
}
