    (function () {
        var page = document.getElementById('portfolio-page');
        if (!page) return;

        // Restore the original hover/click cards with keyboard support and a CSS-only fallback.
        var initialTag = (new URLSearchParams(window.location.search).get('tag') || '').trim();
        page.setAttribute('data-initial-tag', initialTag);

        var grid = document.getElementById('portfolio-grid');
        var empty = document.getElementById('portfolio-empty');
        var status = document.getElementById('portfolio-status');
        page.querySelector('.portfolio-filters').hidden = false;
        var pills = page.querySelectorAll('.portfolio-pill');
        var cardTags = page.querySelectorAll('.portfolio-card-tag');
        var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        var layoutRaf = null;
        var resizeObserver = typeof window.ResizeObserver === 'function' ? new window.ResizeObserver(function () {
            queueGridLayout();
        }) : null;

        function getCards() {
            return grid ? grid.querySelectorAll('.portfolio-card') : [];
        }

        function setActivePill(filterValue) {
            pills.forEach(function (pill) {
                var value = (pill.getAttribute('data-filter') || '').trim();
                var active = value === filterValue;
                pill.classList.toggle('portfolio-pill--active', active);
                pill.setAttribute('aria-pressed', active ? 'true' : 'false');
            });
        }

        function filterProjects(tagName) {
            var cards = getCards();
            var visible = 0;
            var tag = (tagName || '').trim().toLowerCase();
            cards.forEach(function (card) {
                var tagsList = JSON.parse(card.dataset.tags).map(function (tag) { return tag.toLowerCase(); });
                var show = !tag || tagsList.indexOf(tag) !== -1;
                card.classList.toggle('portfolio-card--hidden', !show);
                card.hidden = !show;
                if (show) visible++;
            });
            layoutPortfolioGrid();
            initializeAllCardDescriptions();
            queueGridLayout();
            status.textContent = visible + (visible === 1 ? ' project' : ' projects') + (tagName ? ' tagged ' + tagName : '');
            if (empty) {
                empty.hidden = visible > 0;
                empty.setAttribute('aria-live', 'polite');
            }
            return visible;
        }

        function updateUrl(tagName) {
            var url = new URL(window.location.href);
            if (tagName) url.searchParams.set('tag', tagName);
            else url.searchParams.delete('tag');
            window.history.replaceState({ tag: tagName || null }, '', url);
        }

        function applyFilter(tagName) {
            var value = (tagName || '').trim();
            pills.forEach(function (pill) {
                if (pill.dataset.filter.toLowerCase() === value.toLowerCase()) value = pill.dataset.filter;
            });
            setActivePill(value);
            filterProjects(value);
            updateUrl(value);
        }

        function getColumnCount() {
            var width = window.innerWidth || document.documentElement.clientWidth || 0;
            if (width >= 1280) return 3;
            if (width >= 640) return 2;
            return 1;
        }

        function getColumnGap() {
            var width = window.innerWidth || document.documentElement.clientWidth || 0;
            if (width >= 1024) return 24;
            if (width >= 640) return 20;
            return 16;
        }

        function getVisibleCards() {
            return Array.prototype.slice.call(getCards()).filter(function (card) {
                return !card.classList.contains('portfolio-card--hidden');
            });
        }

        function layoutPortfolioGrid() {
            if (!grid) return;
            var cards = getVisibleCards();
            if (!cards.length) {
                grid.style.height = '0px';
                return;
            }

            var columns = getColumnCount();
            var gap = getColumnGap();
            var gridWidth = grid.clientWidth;
            if (!gridWidth) return;
            var cardWidth = (gridWidth - (gap * (columns - 1))) / columns;
            var columnHeights = [];
            var i;
            for (i = 0; i < columns; i++) {
                columnHeights.push(0);
            }

            cards.forEach(function (card, index) {
                card.style.width = cardWidth + 'px';
                var columnIndex = index < columns ? index : 0;
                if (index >= columns) {
                    var minHeight = columnHeights[0];
                    columnIndex = 0;
                    for (i = 1; i < columns; i++) {
                        if (columnHeights[i] < minHeight) {
                            minHeight = columnHeights[i];
                            columnIndex = i;
                        }
                    }
                }

                var x = columnIndex * (cardWidth + gap);
                var y = columnHeights[columnIndex];
                card.style.transform = 'translate(' + x + 'px, ' + y + 'px)';
                columnHeights[columnIndex] = y + card.offsetHeight + gap;
            });

            var maxHeight = 0;
            columnHeights.forEach(function (h) {
                if (h > maxHeight) maxHeight = h;
            });
            grid.style.height = Math.max(0, maxHeight - gap) + 'px';
        }

        function queueGridLayout() {
            if (layoutRaf) window.cancelAnimationFrame(layoutRaf);
            layoutRaf = window.requestAnimationFrame(function () {
                layoutRaf = null;
                layoutPortfolioGrid();
            });
        }

        function getCardDescription(card) {
            return card.querySelector('.portfolio-card-description');
        }

        function applyCollapsedDescription(desc) {
            desc.style.flex = '0 0 auto';
            desc.style.display = '-webkit-box';
            desc.style.webkitBoxOrient = 'vertical';
            desc.style.webkitLineClamp = '3';
            desc.style.overflow = 'hidden';
        }

        function applyExpandedDescription(desc) {
            desc.style.flex = '0 0 auto';
            desc.style.display = 'block';
            desc.style.webkitBoxOrient = '';
            desc.style.webkitLineClamp = '';
            desc.style.overflow = 'visible';
        }

        function clearDescriptionAnimationState(desc) {
            var timeoutId = desc.getAttribute('data-transition-timeout');
            if (timeoutId) {
                window.clearTimeout(Number(timeoutId));
                desc.removeAttribute('data-transition-timeout');
            }
            desc.style.maxHeight = '';
            desc.style.transition = '';
        }

        function measureCollapsedHeight(desc) {
            var clone = desc.cloneNode(true);
            clone.removeAttribute('id');
            var width = desc.getBoundingClientRect().width;
            applyCollapsedDescription(clone);
            clone.style.position = 'absolute';
            clone.style.visibility = 'hidden';
            clone.style.pointerEvents = 'none';
            clone.style.left = '-9999px';
            clone.style.top = '0';
            clone.style.width = width + 'px';
            clone.style.maxHeight = '';
            clone.style.transition = 'none';
            document.body.appendChild(clone);
            var h = clone.getBoundingClientRect().height;
            document.body.removeChild(clone);
            return h;
        }

        function measureExpandedHeight(desc) {
            var clone = desc.cloneNode(true);
            clone.removeAttribute('id');
            var width = desc.getBoundingClientRect().width;
            applyExpandedDescription(clone);
            clone.style.position = 'absolute';
            clone.style.visibility = 'hidden';
            clone.style.pointerEvents = 'none';
            clone.style.left = '-9999px';
            clone.style.top = '0';
            clone.style.width = width + 'px';
            clone.style.maxHeight = '';
            clone.style.transition = 'none';
            document.body.appendChild(clone);
            var h = clone.getBoundingClientRect().height;
            document.body.removeChild(clone);
            return h;
        }

        function isDescriptionTruncated(desc) {
            var collapsedHeight = measureCollapsedHeight(desc);
            var expandedHeight = measureExpandedHeight(desc);
            var lineHeight = parseFloat(window.getComputedStyle(desc).lineHeight) || 16;
            var threshold = Math.max(2, lineHeight * 0.35);
            return expandedHeight - collapsedHeight > threshold;
        }

        function isCardExpandable(card) {
            return card.getAttribute('data-expandable') === 'true';
        }

        function setCardExpandable(card, expandable) {
            card.setAttribute('data-expandable', expandable ? 'true' : 'false');
            card.classList.toggle('portfolio-card--expandable', expandable);
            var description = getCardDescription(card);
            if (description && expandable) {
                description.setAttribute('tabindex', '0');
                description.setAttribute('role', 'button');
                description.setAttribute('aria-expanded', String(card.classList.contains('portfolio-card--expanded')));
            } else if (description) {
                ['tabindex', 'role', 'aria-expanded'].forEach(function (attribute) { description.removeAttribute(attribute); });
            }
        }

        function initializeCardDescription(card) {
            var description = getCardDescription(card);
            if (!description) {
                setCardExpandable(card, false);
                return;
            }

            clearDescriptionAnimationState(description);

            applyExpandedDescription(description);
            var expandable = isDescriptionTruncated(description);
            setCardExpandable(card, expandable);

            if (expandable) {
                var shouldStayExpanded = card.classList.contains('portfolio-card--expanded');
                if (shouldStayExpanded) {
                    applyExpandedDescription(description);
                } else {
                    applyCollapsedDescription(description);
                }
            } else {
                card.classList.remove('portfolio-card--expanded');
                card.classList.remove('portfolio-card--pinned');
                applyExpandedDescription(description);
            }
        }

        function animateDescription(desc, expand) {
            clearDescriptionAnimationState(desc);

            if (prefersReducedMotion) {
                if (expand) {
                    applyExpandedDescription(desc);
                } else {
                    applyCollapsedDescription(desc);
                }
                desc.style.maxHeight = '';
                desc.style.transition = '';
                return;
            }

            var startHeight = desc.getBoundingClientRect().height;
            var endHeight = 0;

            if (expand) {
                applyExpandedDescription(desc);
                endHeight = desc.getBoundingClientRect().height;
            } else {
                endHeight = measureCollapsedHeight(desc);
                applyExpandedDescription(desc);
            }

            desc.style.overflow = 'hidden';
            desc.style.maxHeight = startHeight + 'px';
            desc.style.transition = 'none';
            desc.getBoundingClientRect();

            desc.style.transition = 'max-height 350ms cubic-bezier(0.22, 1, 0.36, 1)';
            desc.style.maxHeight = endHeight + 'px';

            var timeoutId = window.setTimeout(function () {
                desc.style.transition = '';
                desc.style.maxHeight = '';
                if (expand) {
                    applyExpandedDescription(desc);
                    desc.style.overflow = 'visible';
                } else {
                    applyCollapsedDescription(desc);
                    desc.style.overflow = 'hidden';
                }
                desc.removeAttribute('data-transition-timeout');
            }, 380);
            desc.setAttribute('data-transition-timeout', String(timeoutId));
        }

        function setCardExpanded(card, expanded) {
            var description = getCardDescription(card);
            if (!description) return;
            if (!isCardExpandable(card)) return;
            var isExpanded = card.classList.contains('portfolio-card--expanded');
            if (isExpanded === expanded) return;
            card.classList.toggle('portfolio-card--expanded', expanded);
            description.setAttribute('aria-expanded', String(expanded));
            animateDescription(description, expanded);
            queueGridLayout();
        }

        function attachCardInteractions(card) {
            var hoverTimer = null;
            var description = getCardDescription(card);
            description.addEventListener('keydown', function (event) {
                if (event.key !== 'Enter' && event.key !== ' ') return;
                if (!isCardExpandable(card)) return;
                event.preventDefault();
                var expanded = !card.classList.contains('portfolio-card--expanded');
                card.classList.toggle('portfolio-card--pinned', expanded);
                setCardExpanded(card, expanded);
            });

            card.addEventListener('mouseenter', function () {
                if (!isCardExpandable(card)) return;
                if (card.classList.contains('portfolio-card--pinned')) return;
                if (hoverTimer) window.clearTimeout(hoverTimer);
                hoverTimer = window.setTimeout(function () {
                    setCardExpanded(card, true);
                }, 3000);
            });

            card.addEventListener('mouseleave', function () {
                if (hoverTimer) {
                    window.clearTimeout(hoverTimer);
                    hoverTimer = null;
                }
                if (!isCardExpandable(card)) return;
                if (!card.classList.contains('portfolio-card--pinned') && card.classList.contains('portfolio-card--expanded')) {
                    setCardExpanded(card, false);
                }
            });

            card.addEventListener('click', function (e) {
                if (e.target.closest('a, button')) return;
                if (!isCardExpandable(card)) return;
                var pinned = card.classList.contains('portfolio-card--pinned');
                card.classList.toggle('portfolio-card--pinned', !pinned);
                setCardExpanded(card, !pinned);
            });
        }

        function handlePillClick(e) {
            var pill = e.target.closest('.portfolio-pill');
            if (!pill) return;
            e.preventDefault();
            var filter = (pill.getAttribute('data-filter') || '').trim();
            applyFilter(filter);
        }

        function handleCardTagClick(e) {
            var btn = e.target.closest('.portfolio-card-tag');
            if (!btn) return;
            e.preventDefault();
            var filter = (btn.getAttribute('data-filter') || '').trim();
            pills.forEach(function (pill) { if (pill.dataset.filter === filter) pill.focus({ preventScroll: true }); });
            applyFilter(filter);
        }

        pills.forEach(function (pill) {
            pill.addEventListener('click', handlePillClick);
        });
        cardTags.forEach(function (btn) {
            btn.disabled = false;
            btn.addEventListener('click', handleCardTagClick);
        });

        function initializeAllCardDescriptions() {
            getCards().forEach(function (card) {
                if (!card.hidden) initializeCardDescription(card);
            });
        }

        getCards().forEach(function (card) {
            attachCardInteractions(card);
            if (resizeObserver) {
                resizeObserver.observe(card);
            }
        });
        grid.classList.add('portfolio-grid--enhanced');
        layoutPortfolioGrid();
        initializeAllCardDescriptions();
        queueGridLayout();

        var resizeTimer = null;
        function scheduleDescriptionRecalculation() {
            if (resizeTimer) window.clearTimeout(resizeTimer);
            resizeTimer = window.setTimeout(function () {
                window.requestAnimationFrame(function () {
                    layoutPortfolioGrid();
                    initializeAllCardDescriptions();
                    queueGridLayout();
                });
            }, 180);
        }

        window.addEventListener('resize', scheduleDescriptionRecalculation);
        if (document.fonts) document.fonts.ready.then(scheduleDescriptionRecalculation);
        window.addEventListener('popstate', function () {
            applyFilter(new URLSearchParams(location.search).get('tag') || '');
        });

        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', scheduleDescriptionRecalculation);
        }

        if (initialTag) {
            applyFilter(initialTag);
        } else {
            setActivePill('');
            filterProjects('');
        }
    })();
