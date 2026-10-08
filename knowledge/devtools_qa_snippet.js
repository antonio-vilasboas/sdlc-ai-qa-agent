// Recolha manual de seletores data-test no Swag Labs (Chrome DevTools → Console).
// Uso: colar a definição uma vez; em cada ecrã executar qa('<nome_do_ecra>');
// no fim, copy(localStorage.getItem('qa_kb')) copia a recolha para a área de transferência.
// Resultado versionado em knowledge/recolha_devtools.json.
qa = (nome) => {
  const d = JSON.parse(localStorage.getItem('qa_kb') || '{}');
  d[nome] = {
    url: location.pathname,
    elementos: [...document.querySelectorAll('[data-test]')].map(e => [
      e.tagName.toLowerCase(),
      e.dataset.test,
      e.tagName === 'SELECT'
        ? [...e.options].map(o => `${o.value}=${o.text}`).join(' | ')
        : (e.innerText || e.value || '').trim().replace(/\s+/g, ' ').slice(0, 100)
    ])
  };
  localStorage.setItem('qa_kb', JSON.stringify(d));
  console.log(`✅ ${nome}: ${d[nome].elementos.length} elementos guardados`);
};
