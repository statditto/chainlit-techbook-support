(() => {
  const SELECTORS = {
    aiMessage: '.message-content',
    userBubble: 'div.px-5.py-2\\.5.relative.bg-accent.rounded-3xl.max-w-\\[70\\%\\].flex-grow-0'
  };

  const CLASS_NAMES = {
    target: 'cl-anim-target',
    active: 'cl-anim-enter-active',
    done: 'cl-anim-done'
  };

  const DATA_ATTR = {
    animated: 'clAnimated'
  };

  const ENTER_DURATION_MS = 700;
  const OBSERVER_ROOT = document.body;

  const LOGO_LAYERS = [
    "/public/logos/ring-01.svg",
    "/public/logos/ring-02.svg",
    "/public/logos/ring-03.svg",
    "/public/logos/ring-04.svg",
    "/public/logos/ring-05.svg",
    "/public/logos/ring-06.svg",
    "/public/logos/ring-07.svg",
    "/public/logos/ring-08.svg"
  ];

  /** レイヤードロゴのコンテナ要素を生成する共通ヘルパー */
  function createLogoContainer(className) {
    const container = document.createElement('div');
    container.className = className;
    container.setAttribute('aria-hidden', 'true');

    LOGO_LAYERS.forEach((src, i) => {
      const layer = document.createElement('img');
      layer.src = src;
      layer.alt = '';
      layer.className = `cl-logo-layer cl-logo-layer-${i + 1}`;
      container.appendChild(layer);
    });

    return container;
  }

  function replaceLoginLogo() {
    const form = document.querySelector('form:has(input[type="password"])');
    if (!form) return;
    if (form.dataset.clLogoInjected === 'true') return;

    form.prepend(createLogoContainer('cl-layered-logo'));
    form.dataset.clLogoInjected = 'true';

    debugLog('login logo injected');
  }

  function replaceStandardLogos() {
    const logos = document.querySelectorAll('img.logo[src="/public/logo.svg"]');
    if (!logos.length) return;

    logos.forEach((img) => {
      if (!(img instanceof HTMLElement)) return;
      if (img.dataset.clLogoReplaced === 'true') return;

      img.replaceWith(createLogoContainer('cl-layered-logo cl-layered-logo-inline'));
      img.dataset.clLogoReplaced = 'true';

      debugLog('standard logo replaced');
    });
  }

  function isElement(node) {
    return node instanceof HTMLElement;
  }

  function debugLog(...args) {
    console.log('[chainlit-effects]', ...args);
  }

  function logMutationSummary(mutation) {
    if (mutation.type === 'childList') {
      debugLog('mutation childList', {
        addedNodes: mutation.addedNodes.length,
        removedNodes: mutation.removedNodes.length,
        target: mutation.target
      });
      return;
    }

    if (mutation.type === 'characterData') {
      debugLog('mutation characterData', {
        value: mutation.target?.textContent,
        parent: mutation.target?.parentElement
      });
    }
  }

  function isAnimated(element) {
    return element.dataset[DATA_ATTR.animated] === 'true';
  }

  function isAnimating(element) {
    return element.dataset[DATA_ATTR.animated] === 'pending';
  }

  function isAiMessage(element) {
    return isElement(element) && element.matches(SELECTORS.aiMessage);
  }

  function getElementText(element) {
    if (!isElement(element)) return '';
    return (element.textContent || '').trim();
  }

  function hasRenderableContent(element) {
    if (!isElement(element)) return false;

    if (isAiMessage(element)) {
      return getElementText(element).length > 0;
    }

    return true;
  }

  function findClosestAnimatedTarget(node) {
    if (!node) return null;

    const baseElement = isElement(node) ? node : node.parentElement;
    if (!baseElement) return null;

    return baseElement.closest(`${SELECTORS.aiMessage}, ${SELECTORS.userBubble}`);
  }

  function markAsDone(element) {
    element.dataset[DATA_ATTR.animated] = 'true';
    element.classList.remove(CLASS_NAMES.active);
    element.classList.add(CLASS_NAMES.done);
    debugLog('animation done', element);
  }

  function animateElement(element) {
    if (!isElement(element)) return;
    if (!hasRenderableContent(element)) return;
    if (isAnimated(element) || isAnimating(element)) return;

    element.dataset[DATA_ATTR.animated] = 'pending';
    element.classList.add(CLASS_NAMES.target);
    element.classList.remove(CLASS_NAMES.done);

    debugLog('animation start', element);

    requestAnimationFrame(() => {
      void element.offsetWidth;
      requestAnimationFrame(() => {
        element.classList.add(CLASS_NAMES.active);
      });
    });

    window.setTimeout(() => {
      markAsDone(element);
    }, ENTER_DURATION_MS);
  }

  function collectTargetsFromNode(node) {
    const targets = [];

    if (isElement(node)) {
      if (node.matches(SELECTORS.aiMessage) || node.matches(SELECTORS.userBubble)) {
        targets.push(node);
      }

      targets.push(...node.querySelectorAll(SELECTORS.aiMessage));
      targets.push(...node.querySelectorAll(SELECTORS.userBubble));
    }

    const closestTarget = findClosestAnimatedTarget(node);
    if (closestTarget) {
      targets.push(closestTarget);
    }

    return [...new Set(targets)];
  }

  function handleMutations(mutations) {
    mutations.forEach((mutation) => {
      replaceLoginLogo();
      replaceStandardLogos();
      logMutationSummary(mutation);

      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach((node) => {
          const targets = collectTargetsFromNode(node);
          targets.forEach(animateElement);
        });
      }

      if (mutation.type === 'characterData') {
        const targets = collectTargetsFromNode(mutation.target);
        targets.forEach(animateElement);
      }
    });
  }

  function startObserver() {
    const observer = new MutationObserver(handleMutations);

    observer.observe(OBSERVER_ROOT, {
      childList: true,
      subtree: true,
      characterData: true
    });
  }

  function init() {
    replaceLoginLogo();
    replaceStandardLogos();
    startObserver();
    debugLog('observer started');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();