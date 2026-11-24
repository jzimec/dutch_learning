/* Dutch Learning Word: bookmark current position and collect review words.
   Local to this browser. Does not alter quiz progress or other modules. */
(function () {
  'use strict';
  const userId = () => window.dutchAuth?.currentUserId?.() || null;
  const POS_KEY = 'dutchWordBookmarkV1';
  const NOTE_KEY = 'dutchWordNotebookV1';
  const scoped = key => userId() ? key + ':' + userId() : null;
  const read = (key, fallback) => {
    try { if (!userId()) return fallback; const data = JSON.parse(localStorage.getItem(scoped(key))); return data ?? fallback; }
    catch { return fallback; }
  };
  const write = (key, value) => {
    try { if (!userId()) { alert('请先登录后使用书签和笔记本。'); return false; } localStorage.setItem(scoped(key), JSON.stringify(value)); return true; }
    catch { alert('无法保存：请检查浏览器存储空间。'); return false; }
  };
  const lesson = () => typeof current === 'function' ? current() : null;
  const position = () => {
    const l = lesson();
    const cat = typeof category !== 'undefined' ? category : null;
    return l && cat && Array.isArray(lessonsData[cat]) ? {cat, nl: l.nl} : null;
  };
  const notebook = () => {
    const data = read(NOTE_KEY, []);
    return Array.isArray(data) ? data.filter(x => x && typeof x.cat === 'string' && typeof x.nl === 'string') : [];
  };
  const match = (entry) => {
    if (typeof lessonsData === 'undefined' || !lessonsData || !Array.isArray(lessonsData[entry.cat])) return -1;
    return lessonsData[entry.cat].findIndex(l => l.nl === entry.nl);
  };
  const jump = (entry) => {
    const idx = match(entry);
    if (idx < 0) { alert('该单词已不在当前词库中。'); return; }
    closePanel();
    openLesson(entry.cat, idx);
  };
  function closePanel() { document.getElementById('word-notebook-panel')?.remove(); }
  function refresh() {
    const currentPos = userId() ? position() : null;
    const saved = read(POS_KEY, null);
    const items = notebook();
    const noteBtn = document.getElementById('word-note-add');
    const markBtn = document.getElementById('word-bookmark-save');
    const resumeBtn = document.getElementById('word-bookmark-resume');
    if (noteBtn) {
      noteBtn.disabled = !userId();
      const exists = currentPos && items.some(x => x.cat === currentPos.cat && x.nl === currentPos.nl);
      noteBtn.textContent = exists ? '✓ 已加入笔记本' : '＋ 加入笔记本';
      noteBtn.setAttribute('aria-pressed', String(!!exists));
    }
    if (markBtn) markBtn.disabled = !userId();
    if (markBtn) markBtn.textContent = saved && currentPos && saved.cat === currentPos.cat && saved.nl === currentPos.nl ? '✓ 已设为书签' : '设为书签';
    if (resumeBtn) { resumeBtn.disabled = !userId() || !saved || match(saved) < 0; resumeBtn.title = saved ? '点击直接跳转：' + saved.nl : '还没有书签'; }
    const count = document.getElementById('word-notebook-count');
    if (count) count.textContent = String(items.length);
    refreshHomeBookmark();
  }
  function refreshHomeBookmark() {
    const grid = document.querySelector('#specialView .category-grid');
    if (!grid || document.querySelector('#specialView.hidden')) return;
    const saved = read(POS_KEY, null);
    let button = document.getElementById('word-home-bookmark');
    if (!saved || match(saved) < 0) {
      if (button) button.remove();
      return;
    }
    if (!button) {
      button = document.createElement('button');
      button.type = 'button';
      button.id = 'word-home-bookmark';
      button.className = 'category-card word-home-bookmark';
      grid.insertBefore(button, grid.firstChild);
    }
    button.textContent = '🔖 继续上次：' + saved.nl + ' · 点击直接跳转';
    button.onclick = () => jump(read(POS_KEY, null));
  }
  function showNotebook() {
    closePanel();
    if (!userId()) { alert('请先登录后查看笔记本。'); return; }
    const panel = document.createElement('div');
    panel.id = 'word-notebook-panel';
    panel.className = 'word-tools-overlay';
    panel.innerHTML = '<section class="word-tools-dialog" role="dialog" aria-modal="true" aria-label="复习笔记本"><header><strong>📒 复习笔记本</strong><button type="button" id="word-note-close" aria-label="关闭">×</button></header><p class="word-tools-hint">保存在当前浏览器中；不会自动同步到其他设备。</p><div id="word-note-list"></div></section>';
    document.body.appendChild(panel);
    panel.addEventListener('click', e => { if (e.target === panel) closePanel(); });
    panel.querySelector('#word-note-close').onclick = closePanel;
    const list = panel.querySelector('#word-note-list');
    const items = notebook();
    if (!items.length) { list.textContent = '还没有收藏单词。打开 Word，点击「加入笔记本」。'; return; }
    items.forEach(entry => {
      const row = document.createElement('div');
      row.className = 'word-tools-entry';
      const title = document.createElement('button');
      title.type = 'button';
      title.className = 'word-tools-open';
      title.textContent = entry.nl + (entry.en ? ' · ' + entry.en : '') + (entry.zh ? ' · ' + entry.zh : '');
      title.onclick = () => jump(entry);
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.textContent = '移除';
      remove.setAttribute('aria-label', '从笔记本移除 ' + entry.nl);
      remove.onclick = () => { write(NOTE_KEY, notebook().filter(x => !(x.cat === entry.cat && x.nl === entry.nl))); showNotebook(); refresh(); };
      row.append(title, remove);
      list.appendChild(row);
    });
  }
  function installStyle(){if(document.getElementById('word-tools-style'))return;const style=document.createElement('style');style.id='word-tools-style';style.textContent=".word-tools-controls{display:flex;flex-wrap:wrap;gap:5px;justify-content:flex-end;margin:0 0 6px}.word-tools-controls button{font:inherit;font-size:12px;border:1px solid #9bb5db;background:#fff;border-radius:8px;padding:5px 7px;cursor:pointer;color:#16406f}.word-tools-controls button:disabled{opacity:.45}.word-tools-overlay{position:fixed;inset:0;z-index:12000;background:rgba(0,0,0,.5);display:flex;justify-content:center;align-items:center;padding:12px}.word-tools-dialog{background:#fff;color:#192536;border-radius:14px;width:min(520px,100%);max-height:85vh;overflow:auto;padding:16px}.word-tools-dialog header{display:flex;justify-content:space-between;align-items:center}.word-tools-dialog header button{font-size:25px;border:0;background:transparent}.word-tools-hint{font-size:12px;color:#536273}.word-tools-entry{display:flex;gap:8px;align-items:center;justify-content:space-between;border-top:1px solid #e5e8ee;padding:8px 0}.word-tools-open{flex:1;text-align:left;border:0;background:transparent;color:#174d85}@media(max-width:600px){.word-tools-controls{justify-content:center}.word-tools-controls button{font-size:11px;padding:4px 6px}}";document.head.appendChild(style);}
  function init() {
    installStyle();
    const card = document.querySelector('.word-card');
    if (!card || document.getElementById('word-note-add')) return;
    const controls = document.createElement('div');
    controls.className = 'word-tools-controls';
    controls.innerHTML = '<button type="button" id="word-bookmark-save" title="把当前单词设为书签">设为书签</button><button type="button" id="word-bookmark-resume" title="点击直接跳到书签单词">🔖 跳到书签</button><button type="button" id="word-note-add">＋ 加入笔记本</button><button type="button" id="word-notebook-open">📒 笔记本 <span id="word-notebook-count">0</span></button>';
    card.insertBefore(controls, card.querySelector('.split-2'));
    controls.querySelector('#word-bookmark-save').onclick = () => { const p = position(); if (p && write(POS_KEY, p)) refresh(); };
    controls.querySelector('#word-bookmark-resume').onclick = () => { const p = read(POS_KEY, null); if (p) jump(p); };
    controls.querySelector('#word-note-add').onclick = () => {
      const p = position(), l = lesson(); if (!p || !l) return;
      const items = notebook(), exists = items.some(x => x.cat === p.cat && x.nl === p.nl);
      const next = exists ? items.filter(x => !(x.cat === p.cat && x.nl === p.nl)) : [...items, {...p, en:l.en, zh:l.zh}];
      if (write(NOTE_KEY, next)) refresh();
    };
    controls.querySelector('#word-notebook-open').onclick = showNotebook;
    const word = document.getElementById('nlWord');
    if (word) new MutationObserver(refresh).observe(word, {childList:true, characterData:true, subtree:true});
    const special = document.getElementById('specialView');
    if (special) new MutationObserver(() => refreshHomeBookmark()).observe(special, {childList:true});
    window.addEventListener('dutch-auth-change', () => { closePanel(); refresh(); });
    window.addEventListener('pageshow', refresh);
    refresh();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once:true});
  else init();
  window.dutchWordTools = {refresh};
})();
