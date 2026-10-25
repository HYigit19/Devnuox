/* Interactive demos. All data is fictional and lives in window.NX_DEMO (per language). */
(function () {
  var D = window.NX_DEMO;
  if (!D) return;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  /* ---------- 1. Request assistant ---------- */
  (function () {
    var root = document.getElementById("demo-assist");
    if (!root) return;
    var A = D.assist, current = 0, runId = 0;

    var inbox = el("div", "dx-inbox");
    inbox.appendChild(el("p", "dx-label", A.inbox));
    var list = el("div", "dx-list");
    inbox.appendChild(list);
    var pane = el("div", "dx-pane");
    root.appendChild(inbox);
    root.appendChild(pane);

    A.mails.forEach(function (m, i) {
      var b = el("button", "dx-mail");
      b.type = "button";
      b.id = "dx-mail-" + i;
      var top = el("span", "dx-mail-top");
      top.appendChild(el("b", null, m.from.split(" · ")[0]));
      top.appendChild(el("span", "dx-time", m.time));
      b.appendChild(top);
      b.appendChild(el("span", "dx-subj", m.subject));
      b.addEventListener("click", function () { select(i, true); });
      list.appendChild(b);
    });

    function select(i, focusPane) {
      current = i; runId++;
      list.querySelectorAll(".dx-mail").forEach(function (b, k) { b.setAttribute("aria-pressed", String(k === i)); });
      var m = A.mails[i];
      pane.innerHTML = "";
      var mail = el("div", "dx-email");
      mail.appendChild(el("p", "dx-from", m.from));
      mail.appendChild(el("h3", "dx-h", m.subject));
      mail.appendChild(el("p", "dx-body", m.body));
      var btn = el("button", "btn btn-primary", A.analyze);
      btn.type = "button";
      var res = el("div", "dx-result");
      btn.addEventListener("click", function () { analyze(m, btn, res); });
      mail.appendChild(btn);
      pane.appendChild(mail);
      pane.appendChild(res);
      if (focusPane && window.innerWidth < 760) pane.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    }

    function analyze(m, btn, res) {
      var my = ++runId;
      btn.disabled = true;
      btn.textContent = A.analyzing;
      res.innerHTML = "";
      var steps = el("ol", "dx-steps");
      A.steps.forEach(function (s) { steps.appendChild(el("li", null, s)); });
      res.appendChild(steps);
      var items = steps.querySelectorAll("li"), k = 0;
      (function tick() {
        if (my !== runId) return;
        if (k > 0) items[k - 1].className = "done";
        if (k < items.length) { items[k].className = "active"; k++; setTimeout(tick, reduce ? 0 : 420); return; }
        btn.hidden = true;
        show(m, res);
      })();
    }

    function show(m, res) {
      var card = el("div", "dx-card");
      var head = el("div", "dx-card-head");
      head.appendChild(el("b", null, A.fields_h));
      head.appendChild(el("span", "dx-prio " + m.prio, A.prio[m.prio]));
      card.appendChild(head);
      var dl = el("dl", "dx-fields");
      m.fields.forEach(function (f) { dl.appendChild(el("dt", null, f[0])); dl.appendChild(el("dd", null, f[1])); });
      card.appendChild(dl);
      res.appendChild(card);

      var rc = el("div", "dx-card");
      rc.appendChild(el("b", null, A.reply_h));
      var ta = el("textarea", "dx-reply");
      ta.value = m.reply;
      ta.rows = 7;
      ta.id = "dx-reply";
      ta.setAttribute("aria-label", A.reply_h);
      rc.appendChild(ta);
      var ok = el("button", "btn btn-primary", A.approve);
      ok.type = "button";
      var msg = el("p", "dx-ok", A.approved);
      msg.hidden = true;
      ok.addEventListener("click", function () { ok.hidden = true; msg.hidden = false; });
      rc.appendChild(ok);
      rc.appendChild(msg);
      res.appendChild(rc);
    }

    select(0, false);
  })();

  /* ---------- 2. Customer portal ---------- */
  (function () {
    var root = document.getElementById("demo-portal");
    if (!root) return;
    var P = D.portal;
    var orders = P.orders.map(function (o) { return { o: o, stage: o.stage }; });
    var cur = 0;

    var bar = el("div", "dx-portal-bar");
    bar.appendChild(el("span", "dx-dot"));
    bar.appendChild(el("span", null, P.login));
    root.appendChild(bar);
    var grid = el("div", "dx-portal");
    var left = el("div", "dx-orders");
    left.appendChild(el("p", "dx-label", P.orders_h));
    var right = el("div", "dx-order");
    grid.appendChild(left);
    grid.appendChild(right);
    root.appendChild(grid);

    function stageLabel(s) { return s >= P.stages.length - 1 ? P.done : P.stages[s]; }

    function renderList() {
      left.querySelectorAll(".dx-oitem").forEach(function (n) { n.remove(); });
      orders.forEach(function (x, i) {
        var b = el("button", "dx-oitem");
        b.type = "button";
        b.setAttribute("aria-pressed", String(i === cur));
        var t = el("span", "dx-mail-top");
        t.appendChild(el("b", null, "#" + x.o.id));
        t.appendChild(el("span", "dx-chip s" + Math.min(x.stage, 4), stageLabel(x.stage)));
        b.appendChild(t);
        b.appendChild(el("span", "dx-subj", x.o.name));
        b.addEventListener("click", function () { cur = i; render(); });
        left.appendChild(b);
      });
    }

    function renderOrder() {
      var x = orders[cur], o = x.o;
      right.innerHTML = "";
      var h = el("div", "dx-order-head");
      var ht = el("div");
      ht.appendChild(el("p", "dx-from", "#" + o.id + " · " + o.date));
      ht.appendChild(el("h3", "dx-h", o.name));
      h.appendChild(ht);
      right.appendChild(h);

      right.appendChild(el("p", "dx-label", P.timeline_h));
      var tl = el("ol", "dx-timeline");
      P.stages.forEach(function (s, k) {
        var li = el("li", k < x.stage ? "done" : k === x.stage ? (k === P.stages.length - 1 ? "done" : "active") : "");
        li.appendChild(el("span", "dx-tdot"));
        li.appendChild(el("span", null, s));
        tl.appendChild(li);
      });
      right.appendChild(tl);

      var act = el("div", "dx-actions");
      var adv = el("button", "btn btn-primary", P.advance);
      adv.type = "button";
      adv.disabled = x.stage >= P.stages.length - 1;
      adv.addEventListener("click", function () { x.stage = Math.min(x.stage + 1, P.stages.length - 1); render(); });
      var rs = el("button", "btn btn-ghost", P.reset);
      rs.type = "button";
      rs.addEventListener("click", function () { x.stage = o.stage; render(); });
      act.appendChild(adv);
      act.appendChild(rs);
      right.appendChild(act);

      right.appendChild(el("p", "dx-label", P.docs_h));
      var docs = el("ul", "dx-docs");
      var note = el("p", "dx-ok", P.doc_note);
      note.hidden = true;
      o.docs.forEach(function (d) {
        var li = el("li");
        var b = el("button", "dx-doc");
        b.type = "button";
        b.appendChild(el("span", "dx-pdf", "PDF"));
        b.appendChild(el("span", null, d));
        b.addEventListener("click", function () { note.hidden = false; });
        li.appendChild(b);
        docs.appendChild(li);
      });
      right.appendChild(docs);
      right.appendChild(note);
    }

    function render() { renderList(); renderOrder(); }
    render();
  })();

  /* ---------- 3. Dashboard ---------- */
  (function () {
    var root = document.getElementById("demo-dash");
    if (!root) return;
    var S = D.dash;
    var fmtInt = new Intl.NumberFormat(S.locale);
    var fmtMoney = new Intl.NumberFormat(S.locale, { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
    var fmtPct = new Intl.NumberFormat(S.locale, { style: "percent", minimumFractionDigits: 1, maximumFractionDigits: 1 });

    // Deterministic sample data: 24 months per site x product.
    var siteF = { fra: 1.0, muc: 0.8, ham: 0.55 }, prodF = { a: 0.5, b: 0.35, c: 0.15 };
    var prodVal = { a: 2100, b: 5400, c: 900 }, prodRek = { a: 0.021, b: 0.034, c: 0.008 };
    function rev(site, prod, m) { // m: 0..23, 23 = latest month
      var trend = 1 + m * 0.012;
      var season = 1 + 0.08 * Math.sin((m + 2) / 12 * Math.PI * 2);
      var noise = 1 + 0.05 * Math.sin(m * 7.3 + site.length * 3 + prod.charCodeAt(0));
      return 180000 * siteF[site] * prodF[prod] * trend * season * noise;
    }
    function pick(sel, all) { return sel === "all" ? Object.keys(all) : [sel]; }
    function series(site, prod) {
      var out = [];
      for (var m = 0; m < 24; m++) {
        var r = 0, n = 0, rek = 0;
        pick(site, siteF).forEach(function (s) { pick(prod, prodF).forEach(function (p) {
          var v = rev(s, p, m); r += v; var k = v / (prodVal[p] * (1 + 0.004 * m + 0.03 * Math.sin(m * 1.7 + p.charCodeAt(0)))); n += k; rek += k * prodRek[p] * (1 - 0.012 * m + 0.12 * Math.cos(m * 1.3 + s.length));
        }); });
        out.push({ r: r, n: n, rek: rek });
      }
      return out;
    }

    var state = { range: "6", site: "all", product: "all" };
    var filters = el("div", "dx-filters");
    function sel(key, label, opts) {
      var w = el("label", "dx-filter");
      w.appendChild(el("span", null, label));
      var s = el("select");
      s.id = "dx-f-" + key;
      opts.forEach(function (o) { var op = el("option", null, o[1]); op.value = o[0]; s.appendChild(op); });
      s.value = state[key];
      s.addEventListener("change", function () { state[key] = s.value; render(); });
      w.appendChild(s);
      filters.appendChild(w);
    }
    sel("range", S.range, S.ranges);
    sel("site", S.site, S.sites);
    sel("product", S.product, S.products);
    root.appendChild(filters);

    var kpis = el("div", "dx-kpis");
    root.appendChild(kpis);
    var chartWrap = el("div", "dx-chart");
    chartWrap.appendChild(el("p", "dx-label", S.chart));
    var chart = el("div", "dx-bars");
    chart.setAttribute("role", "img");
    chartWrap.appendChild(chart);
    var axis = el("div", "dx-axis");
    chartWrap.appendChild(axis);
    root.appendChild(chartWrap);

    function delta(a, b, isRate) {
      var d = isRate ? (a - b) * 100 : (a - b) / b * 100;
      var sign = Math.abs(d) < 0.05 ? "±" : d >= 0 ? "+" : "−";
      var txt = sign + Math.abs(d).toFixed(1).replace(".", S.locale === "de-DE" ? "," : ".") + (isRate ? (S.locale === "de-DE" ? " Pkt." : " pts") : " %");
      return { txt: txt, good: isRate ? d <= 0 : d >= 0 };
    }

    function render() {
      var n = +state.range, data = series(state.site, state.product);
      var curr = data.slice(24 - n), prev = data.slice(24 - 2 * n, 24 - n);
      function sum(a, k) { return a.reduce(function (t, x) { return t + x[k]; }, 0); }
      var R = sum(curr, "r"), N = sum(curr, "n"), K = sum(curr, "rek");
      var Rp = sum(prev, "r"), Np = sum(prev, "n"), Kp = sum(prev, "rek");
      var vals = [
        [fmtMoney.format(R), delta(R, Rp)],
        [fmtInt.format(Math.round(N)), delta(N, Np)],
        [fmtMoney.format(R / N), delta(R / N, Rp / Np)],
        [fmtPct.format(K / N), delta(K / N, Kp / Np, true)],
      ];
      kpis.innerHTML = "";
      vals.forEach(function (v, i) {
        var t = el("div", "dx-kpi");
        t.appendChild(el("span", null, S.kpis[i]));
        t.appendChild(el("b", null, v[0]));
        t.appendChild(el("small", v[1].good ? "up" : "down", v[1].txt + " " + S.vs));
        kpis.appendChild(t);
      });
      var max = Math.max.apply(null, curr.map(function (x) { return x.r; }));
      var top = Math.ceil(max / 1000 / 20) * 20;
      chart.innerHTML = "";
      [0.5, 1].forEach(function (f) {
        var g = el("span", "dx-gl");
        g.style.bottom = f * 100 + "%";
        g.appendChild(el("i", null, fmtInt.format(top * f)));
        chart.appendChild(g);
      });
      var months = S.months.slice(12 - n);
      curr.forEach(function (x, i) {
        var b = el("div", "dx-bar" + (i === curr.length - 1 ? " now" : ""));
        b.style.height = (x.r / 1000 / top * 100).toFixed(1) + "%";
        b.title = months[i] + ": " + fmtInt.format(Math.round(x.r / 1000));
        chart.appendChild(b);
      });
      chart.setAttribute("aria-label", S.chart + ": " + curr.map(function (x, i) { return months[i] + " " + Math.round(x.r / 1000); }).join(", "));
      axis.innerHTML = "";
      months.forEach(function (m, i) {
        var s = el("span", null, (n === 12 && i % 2) ? "" : m);
        axis.appendChild(s);
      });
    }
    render();
  })();
})();
