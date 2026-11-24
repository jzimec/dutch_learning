/* Dutch Learning Word: bookmark current position and collect review words.
   Local to this browser. Does not alter quiz progress or other modules. */
(function () {
  'use strict';
  const POS_KEY = 'dutchWordBookmarkV1';
  const NOTE_KEY = 'dutchWordNotebookV1';
  const read = (key, fallback) => {
    try { const data = JSON.parse(localStorage.getItem(key)); return data ?? fallback; }
    catch { return fallback; }
  };
  const write = (key, value) => {
    try { localStorage.setItem(key, JSON.stringify(value)); return true; }
    catch { alert('无法保存：请检查浏览器存储空间。'); return false; }
  };
  const lesson = () => typeof current === 'function' ? current() : null;
  const position = () => {
    const l = lesson();
    const selected = document.querySelector('.category.selected');
    const cat = selected && selected.dataset.cat;
    return l && cat ? {cat, nl: l.nl} : null;
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
    const currentPos = position();
    const saved = read(POS_KEY, null);
    const items = notebook();
    const noteBtn = document.getElementById('word-note-add');
    const markBtn = document.getElementById('word-bookmark-save');
    const resumeBtn = document.getElementById('word-bookmark-resume');
    if (noteBtn) {
      const exists = currentPos && items.some(x => x.cat === currentPos.cat && x.nl === currentPos.nl);
      noteBtn.textContent = exists ? '✓ 已加入笔记本' : '＋ 加入笔记本';
      noteBtn.setAttribute('aria-pressed', String(!!exists));
    }
    if (markBtn) markBtn.textContent = saved && currentPos && saved.cat === currentPos.cat && saved.nl === currentPos.nl ? '🔖 已标记' : '🔖 书签';
    if (resumeBtn) { resumeBtn.disabled = !saved || match(saved) < 0; resumeBtn.title = saved ? '返回：' + saved.nl : '还没有书签'; }
    const count = document.getElementById('word-notebook-count');
    if (count) count.textContent = String(items.length);
  }
  function showNotebook() {
    closePanel();
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
  function init() {
    const card = document.querySelector('.word-card');
    if (!card || document.getElementById('word-note-add')) return;
    const controls = document.createElement('div');
    controls.className = 'word-tools-controls';
    controls.innerHTML = '<button type="button" id="word-bookmark-save" title="记住当前看到的单词">🔖 书签</button><button type="button" id="word-bookmark-resume" title="跳转到上次标记的单词">继续上次</button><button type="button" id="word-note-add">＋ 加入笔记本</button><button type="button" id="word-notebook-open">📒 笔记本 <span id="word-notebook-count">0</span></button>';
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
    refresh();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once:true});
  else init();
  window.dutchWordTools = {refresh};
})();
