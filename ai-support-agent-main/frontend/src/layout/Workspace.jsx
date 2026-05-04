import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import AvatarImg from "../components/AvatarImg";
import {
  createConversation,
  fetchMemoryGraph,
  fetchMemoryOverview,
  fetchMessages,
  fetchPersonas,
  listConversations,
  postFeedback,
  probeMemory,
  sendChat,
} from "../services/api";

function formatTime(iso) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function formatAxiosError(e) {
  const d = e?.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => x.msg || JSON.stringify(x)).join("; ");
  if (d && typeof d === "object") return JSON.stringify(d);
  return e?.message || "Request failed";
}

export default function Workspace() {
  const { user, logout } = useAuth();
  const { theme, toggle } = useTheme();

  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [channel, setChannel] = useState("chat");
  const [compare, setCompare] = useState(false);
  const [busy, setBusy] = useState(false);
  const [overview, setOverview] = useState(null);
  const [graph, setGraph] = useState(null);
  const [personas, setPersonas] = useState([]);
  const [probe, setProbe] = useState("");
  const [probeHits, setProbeHits] = useState([]);
  const [lastMeta, setLastMeta] = useState(null);
  const [chatError, setChatError] = useState(null);
  const endRef = useRef(null);

  const refreshSidebar = useCallback(async () => {
    const rows = await listConversations();
    setConversations(rows);
    return rows;
  }, []);

  const refreshMemory = useCallback(async () => {
    try {
      const [o, g, p] = await Promise.all([fetchMemoryOverview(), fetchMemoryGraph(), fetchPersonas()]);
      setOverview(o);
      setGraph(g);
      setPersonas(p.personas || []);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    if (!user?.id) return;
    const bootKey = `workspace_boot_${user.id}`;
    let cancelled = false;

    (async () => {
      const rows = await refreshSidebar();
      if (cancelled) return;

      if (!rows.length) {
        if (sessionStorage.getItem(bootKey)) {
          const again = await refreshSidebar();
          if (!cancelled) setActiveId((cur) => cur ?? (again[0]?.id ?? null));
        } else {
          sessionStorage.setItem(bootKey, "1");
          const c = await createConversation({ title: "New chat", channel: "chat" });
          if (cancelled) return;
          await refreshSidebar();
          if (cancelled) return;
          setActiveId(c.id);
        }
      } else {
        setActiveId((cur) => cur ?? (rows[0]?.id ?? null));
      }

      if (cancelled) return;
      await refreshMemory();
    })();

    return () => {
      cancelled = true;
    };
  }, [refreshSidebar, refreshMemory, user?.id]);

  useEffect(() => {
    if (!activeId) return;
    (async () => {
      const msgs = await fetchMessages(activeId);
      setMessages(msgs);
    })();
  }, [activeId]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  const activeTitle = useMemo(() => {
    const c = conversations.find((x) => x.id === activeId);
    return c?.title || "New chat";
  }, [conversations, activeId]);

  const onNewChat = async () => {
    const c = await createConversation({ title: "New chat", channel });
    await refreshSidebar();
    setActiveId(c.id);
    setMessages([]);
    await refreshMemory();
  };

  const onSend = async () => {
    if (!input.trim() || !activeId || busy) return;
    const text = input.trim();
    setInput("");
    const optimistic = [
      ...messages,
      {
        id: `tmp-user-${Date.now()}`,
        role: "user",
        content: text,
        sentiment: null,
        created_at: new Date().toISOString(),
      },
    ];
    setMessages(optimistic);
    setChatError(null);
    setBusy(true);
    try {
      const res = await sendChat(activeId, {
        message: text,
        channel,
        compare_without_memory: compare,
      });
      const msgs = await fetchMessages(activeId);
      setMessages(msgs);
      setLastMeta(res);
      setChatError(null);
      await refreshMemory();
      await refreshSidebar();
    } catch (e) {
      console.error(e);
      setChatError(formatAxiosError(e));
      setInput(text);
      try {
        const msgs = await fetchMessages(activeId);
        setMessages(msgs);
      } catch {
        setMessages((prev) => prev.filter((m) => !String(m.id).startsWith("tmp-user")));
      }
    } finally {
      setBusy(false);
    }
  };

  const onProbe = async () => {
    if (!probe.trim()) return;
    const data = await probeMemory(probe);
    setProbeHits(data.hits || []);
  };

  const onFeedback = async (messageId, helpful) => {
    if (!activeId) return;
    await postFeedback(activeId, messageId, helpful);
    await refreshMemory();
  };

  return (
    <div className="workspace">
      <aside className="sidebar glass">
        <div className="sidebar-top">
          <div className="logo-row">
            <div className="logo-mark" aria-hidden />
            <div>
              <div className="logo-title">Cognitive</div>
              <div className="logo-sub">Support Agent</div>
            </div>
          </div>
          <button type="button" className="btn primary new-chat" onClick={onNewChat}>
            + New chat
          </button>
        </div>

        <div className="sidebar-section-title">Conversations</div>
        <div className="conv-list">
          {conversations.map((c) => (
            <button
              key={c.id}
              type="button"
              className={`conv-item ${c.id === activeId ? "active" : ""}`}
              onClick={() => setActiveId(c.id)}
            >
              <div className="conv-title">{c.title}</div>
              <div className="conv-meta">
                <span className="pill">{c.channel}</span>
              </div>
            </button>
          ))}
          {!conversations.length && <div className="muted small pad">No chats yet — start one.</div>}
        </div>

        <div className="sidebar-bottom">
          <div className="user-row">
            <AvatarImg seed={user?.avatar_seed || user?.email} size={44} />
            <div className="user-meta">
              <div className="user-name">{user?.display_name}</div>
              <div className="muted tiny">{user?.email}</div>
            </div>
          </div>
          <div className="row-actions">
            <button type="button" className="btn ghost" onClick={toggle} title="Toggle theme">
              {theme === "dark" ? "Light" : "Dark"}
            </button>
            <button type="button" className="btn ghost danger" onClick={logout}>
              Log out
            </button>
          </div>
        </div>
      </aside>

      <main className="chat-pane">
        <header className="chat-header glass">
          <div>
            <div className="chat-title">{activeTitle}</div>
            <div className="muted small">
              Memory-first architecture: transcript + semantic RAG evolve every turn.
            </div>
          </div>
          <div className="header-controls">
            <label className="inline">
              <span className="muted small">Channel</span>
              <select value={channel} onChange={(e) => setChannel(e.target.value)} className="select">
                <option value="chat">Chat</option>
                <option value="email">Email</option>
                <option value="phone">Phone</option>
                <option value="whatsapp">WhatsApp</option>
              </select>
            </label>
            <label className="inline magic">
              <input type="checkbox" checked={compare} onChange={(e) => setCompare(e.target.checked)} />
              <span>Before / after (no-memory baseline)</span>
            </label>
          </div>
        </header>

        <div className="messages">
          {!activeId && <div className="empty-state">Create a new chat to begin.</div>}
          {activeId &&
            messages.map((m) => (
              <div key={m.id} className={`msg-row ${m.role}`}>
                <div className="msg-avatar">
                  {m.role === "assistant" ? (
                    <AvatarImg isAgent size={38} />
                  ) : (
                    <AvatarImg seed={user?.avatar_seed || user?.email} size={38} />
                  )}
                </div>
                <div className="msg-bubble glass">
                  <div className="msg-role">{m.role === "assistant" ? "Agent" : "You"}</div>
                  <div className="msg-text">{m.content}</div>
                  <div className="msg-foot">
                    <span className="muted tiny">{formatTime(m.created_at)}</span>
                    {m.role === "user" && m.sentiment && (
                      <span className="pill sentiment">sentiment: {m.sentiment}</span>
                    )}
                    {m.role === "assistant" && typeof m.id === "number" && (
                      <span className="feedback">
                        <button type="button" className="linkish" onClick={() => onFeedback(m.id, true)}>
                          Helpful
                        </button>
                        <button type="button" className="linkish" onClick={() => onFeedback(m.id, false)}>
                          Not yet
                        </button>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          {busy && (
            <div className="msg-row assistant">
              <div className="msg-avatar">
                <AvatarImg isAgent size={38} />
              </div>
              <div className="msg-bubble glass typing">
                <div className="dots" aria-hidden>
                  <span />
                  <span />
                  <span />
                </div>
                <div className="muted small">Weaving memory + retrieval…</div>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {lastMeta?.comparison_mode && (
          <div className="compare-banner glass">
            <div className="compare-col">
              <div className="pill warn">Baseline (no memory)</div>
              <div className="compare-text">{lastMeta.baseline_reply}</div>
            </div>
            <div className="compare-col">
              <div className="pill ok">Memory-augmented</div>
              <div className="compare-text">{lastMeta.reply}</div>
            </div>
          </div>
        )}

        {chatError && (
          <div className="chat-error glass" role="alert">
            <div className="chat-error-title">Could not get a reply</div>
            <div className="chat-error-body">{chatError}</div>
            <button type="button" className="btn ghost tiny-dismiss" onClick={() => setChatError(null)}>
              Dismiss
            </button>
          </div>
        )}

        <div className="composer glass">
          <textarea
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything — repeats should get sharper answers…"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSend();
              }
            }}
          />
          <button type="button" className="btn primary send" disabled={busy || !activeId} onClick={onSend}>
            Send
          </button>
        </div>
      </main>

      <section className="memory-pane glass">
        <div className="memory-header">
          <h2>Memory studio</h2>
          <p className="muted small">Datastore · trajectory · semantic graph (hybrid view)</p>
        </div>

        <div className="memory-section">
          <h3>Overview</h3>
          {overview ? (
            <div className="stat-grid">
              <div className="stat-card">
                <div className="stat-label">Conversations</div>
                <div className="stat-value">{overview.conversations}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Messages (SQL)</div>
                <div className="stat-value">{overview.total_messages}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Vector points (you)</div>
                <div className="stat-value">{overview.messages_indexed_estimate}</div>
              </div>
              <div className="stat-card wide">
                <div className="stat-label">Efficacy</div>
                <div className="stat-value small">
                  {overview.efficacy?.positive_rate != null
                    ? `Positive rate: ${(overview.efficacy.positive_rate * 100).toFixed(1)}%`
                    : overview.efficacy?.note || "Rate answers with Helpful / Not yet."}
                </div>
              </div>
            </div>
          ) : (
            <div className="muted small">Loading…</div>
          )}
          {lastMeta && (
            <div className="meta-block">
              <div className="pill subtle">Last turn analytics</div>
              <pre className="json-snippet">{JSON.stringify(lastMeta.analytics, null, 2)}</pre>
              {lastMeta.privacy && (
                <div className="muted tiny">Stored in: {lastMeta.privacy.stored_in?.join(", ")}</div>
              )}
            </div>
          )}
        </div>

        <div className="memory-section">
          <h3>Cross-channel graph</h3>
          <div className="graph">
            {graph?.nodes?.length ? (
              <svg viewBox="0 0 320 220" className="graph-svg">
                {graph.edges.map((e, idx) => {
                  const a = graph.nodes.find((n) => n.id === e.source);
                  const b = graph.nodes.find((n) => n.id === e.target);
                  if (!a || !b) return null;
                  const ai = graph.nodes.indexOf(a);
                  const bi = graph.nodes.indexOf(b);
                  const x1 = 40 + (ai % 4) * 70;
                  const y1 = 40 + Math.floor(ai / 4) * 70;
                  const x2 = 40 + (bi % 4) * 70;
                  const y2 = 40 + Math.floor(bi / 4) * 70;
                  return (
                    <line
                      key={idx}
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      className={`graph-edge ${e.kind}`}
                    />
                  );
                })}
                {graph.nodes.map((n, i) => {
                  const x = 30 + (i % 4) * 70;
                  const y = 30 + Math.floor(i / 4) * 70;
                  return (
                    <g key={n.id} transform={`translate(${x},${y})`}>
                      <circle r="16" className="graph-node" />
                      <text x="0" y="36" textAnchor="middle" className="graph-label">
                        {(n.label || "").slice(0, 10)}
                      </text>
                    </g>
                  );
                })}
              </svg>
            ) : (
              <div className="muted small">No graph yet.</div>
            )}
          </div>
        </div>

        <div className="memory-section">
          <h3>Semantic probe (RAG)</h3>
          <div className="probe-row">
            <input
              value={probe}
              onChange={(e) => setProbe(e.target.value)}
              placeholder="Try: billing error, SAML, webhook 429…"
            />
            <button type="button" className="btn ghost" onClick={onProbe}>
              Search memory
            </button>
          </div>
          <div className="hits">
            {probeHits.map((h, i) => (
              <div key={i} className="hit glass">
                <div className="muted tiny">
                  score {h.score?.toFixed?.(3)} · {h.channel || "chat"}
                </div>
                <div className="hit-text">{h.text}</div>
              </div>
            ))}
            {!probeHits.length && <div className="muted small">No probe results yet.</div>}
          </div>
        </div>

        <div className="memory-section">
          <h3>Mock personas (prompts)</h3>
          <div className="personas">
            {personas.map((p) => (
              <div key={p.id} className="persona glass">
                <div className="persona-name">{p.name}</div>
                <div className="muted tiny">{p.archetype}</div>
                <div className="persona-sample">{p.sample_problem}</div>
                <div className="muted tiny">Channels: {p.channels?.join(", ")}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
