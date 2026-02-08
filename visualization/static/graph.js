// D3.js Force-Directed Supply Chain Graph
(function() {
    const svg = d3.select('#graph');
    const tooltip = d3.select('#tooltip');
    const container = document.querySelector('.graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    function getApiBase() {
        const params = new URLSearchParams(location.search);
        const fromQuery = params.get('api');
        const base = fromQuery || window.API_BASE || '';
        return base.replace(/\/$/, '');
    }

    function apiUrl(path) {
        const base = getApiBase();
        return base ? base + path : path;
    }

    function wsBase() {
        const base = getApiBase();
        if (!base) return '';
        try {
            const url = new URL(base);
            return (url.protocol === 'https:' ? 'wss://' : 'ws://') + url.host;
        } catch {
            return '';
        }
    }

    svg.attr('width', width).attr('height', height);

    // Glow filter
    const defs = svg.append('defs');
    const filter = defs.append('filter').attr('id', 'glow');
    filter.append('feGaussianBlur').attr('stdDeviation', 3).attr('result', 'blur');
    filter.append('feMerge').selectAll('feMergeNode')
        .data(['blur', 'SourceGraphic']).enter()
        .append('feMergeNode').attr('in', d => d);

    const g = svg.append('g');

    // Zoom
    const zoom = d3.zoom().scaleExtent([0.3, 4]).on('zoom', e => g.attr('transform', e.transform));
    svg.call(zoom);

    async function loadGraph() {
        let data;
        try {
            const resp = await fetch(apiUrl('/api/graph'));
            data = await resp.json();
        } catch {
            data = getDemoData();
        }
        render(data);
        updateStats(data);
    }

    function render(data) {
        g.selectAll('*').remove();
        const { nodes, links } = data;

        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(d => {
                if (d.type === 'requires') return 120;
                if (d.type === 'supplies') return 150;
                return 200;
            }))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => (d.size || 10) + 10));

        const link = g.selectAll('.link').data(links).enter().append('line')
            .attr('class', d => 'link ' + (d.type || ''))
            .attr('stroke-width', d => d.type === 'ships_to' ? 2 : 1.5);

        const node = g.selectAll('.node').data(nodes).enter().append('g')
            .attr('class', 'node')
            .call(d3.drag()
                .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
                .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
                .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
            );

        node.append('circle')
            .attr('r', 0)
            .attr('fill', d => d.color || '#999')
            .attr('stroke', d => d3.color(d.color || '#999').brighter(0.5))
            .style('filter', d => d.type === 'product' ? 'url(#glow)' : '')
            .on('mouseover', showTooltip)
            .on('mouseout', hideTooltip)
            .transition().duration(800).delay((d, i) => i * 30)
            .attr('r', d => d.size || 10);

        node.append('text')
            .attr('dy', d => (d.size || 10) + 14)
            .attr('text-anchor', 'middle')
            .text(d => d.id.length > 20 ? d.id.substring(0, 18) + '...' : d.id);

        simulation.on('tick', () => {
            link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
            node.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
        });
    }

    function showTooltip(event, d) {
        const nameEl = document.createElement('div');
        nameEl.className = 'name';
        nameEl.textContent = d.id;

        const typeEl = document.createElement('div');
        typeEl.className = 'detail';
        typeEl.textContent = 'Type: ' + d.type;

        const tooltipEl = document.getElementById('tooltip');
        tooltipEl.textContent = '';
        tooltipEl.appendChild(nameEl);
        tooltipEl.appendChild(typeEl);

        if (d.cost) {
            const costEl = document.createElement('div');
            costEl.className = 'detail';
            costEl.textContent = 'Cost: $' + d.cost.toLocaleString();
            tooltipEl.appendChild(costEl);
        }
        if (d.location) {
            const locEl = document.createElement('div');
            locEl.className = 'detail';
            locEl.textContent = 'Location: ' + d.location;
            tooltipEl.appendChild(locEl);
        }
        if (d.category) {
            const catEl = document.createElement('div');
            catEl.className = 'detail';
            catEl.textContent = 'Category: ' + d.category;
            tooltipEl.appendChild(catEl);
        }

        tooltipEl.style.left = (event.pageX + 15) + 'px';
        tooltipEl.style.top = (event.pageY - 10) + 'px';
        tooltipEl.classList.add('visible');
    }

    function hideTooltip() {
        document.getElementById('tooltip').classList.remove('visible');
    }

    function updateStats(data) {
        const components = data.nodes.filter(n => n.type === 'component').length;
        const suppliers = data.nodes.filter(n => n.type === 'supplier').length;
        const routes = data.links.filter(l => l.type === 'ships_to').length;
        const totalCost = data.links.reduce((sum, l) => {
            const raw = (l.price ?? l.total_price ?? l.cost ?? 0);
            const val = (typeof raw === 'number') ? raw : parseFloat(raw);
            return sum + (isNaN(val) ? 0 : val);
        }, 0);
        const maxDelivery = data.links.reduce((max, l) => {
            const raw = (l.delivery ?? l.days ?? l.total_days ?? 0);
            const val = (typeof raw === 'number') ? raw : parseFloat(raw);
            return Math.max(max, isNaN(val) ? 0 : val);
        }, 0);
        document.getElementById('stat-components').textContent = components;
        document.getElementById('stat-suppliers').textContent = suppliers;
        document.getElementById('stat-routes').textContent = routes;
        document.getElementById('stat-cost').textContent = '$' + totalCost.toLocaleString(undefined, { maximumFractionDigits: 0 });
        document.getElementById('stat-delivery').textContent = maxDelivery + ' days';
    }

    function getDemoData() {
        const product = { id: 'Ferrari F8', type: 'product', color: '#ffd700', size: 40 };
        const comps = ['V8 Engine', 'Carbon Chassis', 'Brembo Brakes', 'Pirelli Tires', 'Bosch ECU', 'DCT Transmission', 'LED Lights', 'Exhaust System'].map(
            name => ({ id: name, type: 'component', color: '#00d4ff', size: 20 })
        );
        const supps = ['Precision Motors', 'Brembo S.p.A.', 'Pirelli', 'Bosch', 'ZF Group', 'Magneti Marelli'].map(
            name => ({ id: name, type: 'supplier', color: '#00ff88', size: 15 })
        );
        const nodes = [product, ...comps, ...supps];
        const links = [
            ...comps.map(c => ({ source: product.id, target: c.id, type: 'requires' })),
            { source: 'Precision Motors', target: 'V8 Engine', type: 'supplies' },
            { source: 'Brembo S.p.A.', target: 'Brembo Brakes', type: 'supplies' },
            { source: 'Pirelli', target: 'Pirelli Tires', type: 'supplies' },
            { source: 'Bosch', target: 'Bosch ECU', type: 'supplies' },
            { source: 'ZF Group', target: 'DCT Transmission', type: 'supplies' },
            { source: 'Magneti Marelli', target: 'LED Lights', type: 'supplies' },
            { source: 'Precision Motors', target: 'Ferrari F8', type: 'ships_to' },
            { source: 'Bosch', target: 'Ferrari F8', type: 'ships_to' },
        ];
        return { nodes, links };
    }

    loadGraph();

    // WebSocket for live agent feed and graph updates
    try {
        const base = wsBase();
        const wsUrl = (base ? base : (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host) + '/ws/feed';
        const ws = new WebSocket(wsUrl);
        ws.onmessage = function(event) {
            const msg = JSON.parse(event.data);

            if (msg.graph) {
                render(msg.graph);
                updateStats(msg.graph);
                return;
            }
            if (msg.type === 'graph_update' && msg.graph) {
                render(msg.graph);
                updateStats(msg.graph);
                return;
            }

            const feed = document.getElementById('agent-feed');
            const item = document.createElement('div');
            item.className = 'feed-item';
            const typeSpan = document.createElement('span');
            typeSpan.className = 'type';
            typeSpan.textContent = '[' + msg.type + '] ';
            item.appendChild(typeSpan);
            item.appendChild(document.createTextNode(msg.from + ' → ' + msg.to));
            feed.prepend(item);
            if (feed.children.length > 50) feed.lastChild.remove();
        };
    } catch(e) { console.log('WebSocket not available'); }

    // Run demo from UI
    const runBtn = document.getElementById('run-button');
    const runInput = document.getElementById('run-product');
    const runStatus = document.getElementById('run-status');

    async function pollStatus() {
        try {
            const resp = await fetch(apiUrl('/api/status'));
            const data = await resp.json();
            if (data.running) {
                runStatus.textContent = 'Running...';
                setTimeout(pollStatus, 2000);
            } else {
                runStatus.textContent = data.error ? 'Error: ' + data.error : 'Completed';
                loadGraph();
            }
        } catch {
            runStatus.textContent = 'Status check failed';
        }
    }

    async function triggerRun() {
        const product = (runInput.value || '').trim();
        if (!product) {
            runStatus.textContent = 'Enter a product name';
            return;
        }
        runStatus.textContent = 'Starting...';
        try {
            const resp = await fetch(apiUrl('/api/run'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product }),
            });
            if (!resp.ok) {
                runStatus.textContent = 'Server busy or error';
                return;
            }
            const data = await resp.json();
            if (data.status === 'started') {
                runStatus.textContent = 'Running...';
                pollStatus();
            } else {
                runStatus.textContent = 'Failed to start';
            }
        } catch {
            runStatus.textContent = 'Request failed';
        }
    }

    if (runBtn) {
        runBtn.addEventListener('click', triggerRun);
    }
    if (runInput) {
        runInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') triggerRun();
        });
    }
})();
