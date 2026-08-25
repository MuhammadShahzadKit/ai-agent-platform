import { useEffect, useState } from 'react'
import './App.css'

const navItems = [
  { id: 'dashboard', icon: '▣', label: 'Dashboard' },
  { id: 'agents', icon: '◈', label: 'Agents' },
  { id: 'chat', icon: '◉', label: 'Chat' },
  { id: 'documents', icon: '▣', label: 'Documents' },
  { id: 'conversations', icon: '◷', label: 'Conversations' },
]

function App() {
  const [token, setToken] = useState(
    () => localStorage.getItem('digieemp_token') || '',
  )

  const [currentUser, setCurrentUser] = useState(null)
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)

  const [activePage, setActivePage] = useState('dashboard')

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loginError, setLoginError] = useState('')
  const [loading, setLoading] = useState(false)

  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])

  // Create Agent
  const [showCreateAgent, setShowCreateAgent] = useState(false)
  const [creatingAgent, setCreatingAgent] = useState(false)
  const [createAgentError, setCreateAgentError] = useState('')

  const [agentForm, setAgentForm] = useState({
    name: '',
    role: 'assistant',
    description: '',
    system_prompt: '',
    model: 'qwen2.5:3b',
    temperature: 0,
  })

  // --------------------------------------------------
  // Login
  // --------------------------------------------------

  const login = async (event) => {
    event.preventDefault()

    if (!username.trim() || !password) {
      setLoginError('Please enter your username and password.')
      return
    }

    setLoading(true)
    setLoginError('')

    try {
      const formData = new URLSearchParams()

      formData.append('username', username)
      formData.append('password', password)

      const response = await fetch('/api/users/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed.')
      }

      localStorage.setItem('digieemp_token', data.access_token)
      setToken(data.access_token)
      setPassword('')
    } catch (error) {
      setLoginError(error.message || 'Unable to login.')
    } finally {
      setLoading(false)
    }
  }

  // --------------------------------------------------
  // Logout
  // --------------------------------------------------

  const logout = () => {
    localStorage.removeItem('digieemp_token')

    setToken('')
    setCurrentUser(null)
    setAgents([])
    setSelectedAgent(null)
    setMessages([])
    setActivePage('dashboard')
  }

  // --------------------------------------------------
  // Load authenticated user + agents
  // --------------------------------------------------

  useEffect(() => {
    if (!token) {
      return
    }

    const loadWorkspace = async () => {
      setLoading(true)

      try {
        const headers = {
          Authorization: `Bearer ${token}`,
        }

        const [userResponse, agentsResponse] = await Promise.all([
          fetch('/api/users/me', {
            headers,
          }),
          fetch('/api/agents/', {
            headers,
          }),
        ])

        if (
          userResponse.status === 401 ||
          agentsResponse.status === 401
        ) {
          throw new Error('SESSION_EXPIRED')
        }

        if (!userResponse.ok) {
          throw new Error('Unable to load current user.')
        }

        if (!agentsResponse.ok) {
          throw new Error('Unable to load agents.')
        }

        const userData = await userResponse.json()
        const agentsData = await agentsResponse.json()

        const loadedAgents = Array.isArray(agentsData)
          ? agentsData
          : [agentsData]

        const formattedAgents = loadedAgents.map((agent) => ({
          ...agent,
          status: 'Active',
        }))

        setCurrentUser(userData)
        setAgents(formattedAgents)

        setSelectedAgent((current) => {
          if (current) {
            const updated = formattedAgents.find(
              (agent) => agent.id === current.id,
            )

            if (updated) {
              return updated
            }
          }

          return formattedAgents[0] || null
        })
      } catch (error) {
        if (error.message === 'SESSION_EXPIRED') {
          logout()
          setLoginError(
            'Your session has expired. Please login again.',
          )
        } else {
          setLoginError(
            error.message ||
              'Unable to connect to the backend.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadWorkspace()
  }, [token])

  // --------------------------------------------------
  // Create Agent
  // --------------------------------------------------

  const openCreateAgent = () => {
    setCreateAgentError('')

    setAgentForm({
      name: '',
      role: 'assistant',
      description: '',
      system_prompt:
        'You are a helpful document-based AI assistant.',
      model: 'qwen2.5:3b',
      temperature: 0,
    })

    setShowCreateAgent(true)
  }

  const closeCreateAgent = () => {
    if (creatingAgent) {
      return
    }

    setShowCreateAgent(false)
    setCreateAgentError('')
  }

  const handleAgentFormChange = (event) => {
    const { name, value } = event.target

    setAgentForm((current) => ({
      ...current,
      [name]:
        name === 'temperature'
          ? Number(value)
          : value,
    }))
  }

  const createAgent = async (event) => {
    event.preventDefault()

    if (!agentForm.name.trim()) {
      setCreateAgentError('Agent name is required.')
      return
    }

    if (!token) {
      setCreateAgentError(
        'Your session has expired. Please login again.',
      )
      return
    }

    setCreatingAgent(true)
    setCreateAgentError('')

    try {
      const response = await fetch('/api/agents/', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: agentForm.name.trim(),
          role: agentForm.role.trim() || 'assistant',
          description:
            agentForm.description.trim() ||
            'AI assistant',
          system_prompt:
            agentForm.system_prompt.trim() ||
            'You are a helpful AI assistant.',
          model: agentForm.model.trim() || 'qwen2.5:3b',
          temperature: Number(agentForm.temperature),
        }),
      })

      const data = await response.json()

      if (response.status === 401) {
        logout()
        return
      }

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to create agent.',
        )
      }

      const newAgent = {
        ...data,
        status: 'Active',
      }

      setAgents((current) => [
        ...current,
        newAgent,
      ])

      setSelectedAgent(newAgent)
      setShowCreateAgent(false)

      setAgentForm({
        name: '',
        role: 'assistant',
        description: '',
        system_prompt:
          'You are a helpful document-based AI assistant.',
        model: 'qwen2.5:3b',
        temperature: 0,
      })
    } catch (error) {
      setCreateAgentError(
        error.message || 'Unable to create agent.',
      )
    } finally {
      setCreatingAgent(false)
    }
  }

  // --------------------------------------------------
  // Chat
  // --------------------------------------------------

  const sendMessage = async () => {
    const trimmed = message.trim()

    if (!trimmed || !selectedAgent || !token) {
      return
    }

    setMessages((current) => [
      ...current,
      {
        role: 'user',
        content: trimmed,
      },
    ])

    setMessage('')

    try {
      const response = await fetch(
        `/api/chat/${selectedAgent.id}`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: trimmed,
          }),
        },
      )

      const data = await response.json()

      if (response.status === 401) {
        logout()
        return
      }

      if (!response.ok) {
        throw new Error(
          data.detail || 'Chat request failed.',
        )
      }

      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: data.response,
        },
      ])
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: `Error: ${error.message}`,
        },
      ])
    }
  }

  // --------------------------------------------------
  // Login Screen
  // --------------------------------------------------

  if (!token) {
    return (
      <div className="login-shell">
        <div className="login-card">
          <div className="login-brand">
            <div className="brand-mark">D</div>

            <div>
              <strong>DigiEmp</strong>
              <span>AI Agent Platform</span>
            </div>
          </div>

          <div className="login-heading">
            <p className="eyebrow">WELCOME BACK</p>

            <h1>Sign in to DigiEmp</h1>

            <p>
              Access your AI employees, documents,
              conversations, and knowledge base.
            </p>
          </div>

          <form
            onSubmit={login}
            className="login-form"
          >
            <label>
              Username

              <input
                type="text"
                value={username}
                onChange={(event) =>
                  setUsername(event.target.value)
                }
                placeholder="Enter your username"
                autoComplete="username"
              />
            </label>

            <label>
              Password

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </label>

            {loginError && (
              <div className="login-error">
                {loginError}
              </div>
            )}

            <button
              type="submit"
              className="primary-button login-button"
              disabled={loading}
            >
              {loading
                ? 'Signing in...'
                : 'Sign in'}
            </button>
          </form>

          <div className="login-footer">
            FastAPI • PostgreSQL • RAG
          </div>
        </div>
      </div>
    )
  }

  // --------------------------------------------------
  // Dashboard
  // --------------------------------------------------

  const renderDashboard = () => (
    <div className="page-content">
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            AI AGENT PLATFORM
          </p>

          <h1>
            Good morning{' '}
            {currentUser?.username || 'there'} 👋
          </h1>

          <p className="page-subtitle">
            Manage your digital employees, documents,
            and AI conversations.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={openCreateAgent}
        >
          + Create Agent
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon purple">
            ◈
          </div>

          <div>
            <span>Active Agents</span>
            <strong>{agents.length}</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon blue">
            ▣
          </div>

          <div>
            <span>Documents</span>
            <strong>4</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon green">
            ◉
          </div>

          <div>
            <span>Conversations</span>
            <strong>2</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon orange">
            ⚡
          </div>

          <div>
            <span>System Status</span>
            <strong className="status-text">
              Healthy
            </strong>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Your Agents</h2>

              <p>
                AI employees available in your
                workspace.
              </p>
            </div>

            <button
              className="text-button"
              onClick={() =>
                setActivePage('agents')
              }
            >
              View all →
            </button>
          </div>

          <div className="agent-list">
            {loading ? (
              <p>Loading agents...</p>
            ) : agents.length === 0 ? (
              <p>
                No agents found. Create your first
                agent.
              </p>
            ) : (
              agents.map((agent) => (
                <div
                  className="agent-row"
                  key={agent.id}
                >
                  <div className="agent-avatar">
                    AI
                  </div>

                  <div className="agent-info">
                    <strong>{agent.name}</strong>

                    <span>
                      {agent.description}
                    </span>
                  </div>

                  <span className="active-badge">
                    <i></i>
                    Active
                  </span>

                  <button
                    className="small-button"
                    onClick={() => {
                      setSelectedAgent(agent)
                      setActivePage('chat')
                    }}
                  >
                    Chat
                  </button>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="panel quick-panel">
          <div className="panel-header">
            <div>
              <h2>Quick Actions</h2>

              <p>
                Jump directly to common tasks.
              </p>
            </div>
          </div>

          <div className="quick-actions">
            <button
              onClick={() => {
                if (selectedAgent) {
                  setActivePage('chat')
                } else {
                  openCreateAgent()
                }
              }}
            >
              <span>◉</span>

              <div>
                <strong>
                  Start a conversation
                </strong>

                <small>
                  Talk to your AI agent
                </small>
              </div>
            </button>

            <button
              onClick={() =>
                setActivePage('documents')
              }
            >
              <span>▣</span>

              <div>
                <strong>
                  Upload documents
                </strong>

                <small>
                  Add knowledge to your RAG system
                </small>
              </div>
            </button>

            <button onClick={openCreateAgent}>
              <span>◈</span>

              <div>
                <strong>
                  Create an agent
                </strong>

                <small>
                  Configure a new digital employee
                </small>
              </div>
            </button>
          </div>
        </section>
      </div>

      <section className="panel activity-panel">
        <div className="panel-header">
          <div>
            <h2>Recent Activity</h2>

            <p>
              Latest platform activity.
            </p>
          </div>
        </div>

        <div className="activity-list">
          <div className="activity-item">
            <span className="activity-dot green"></span>

            <div>
              <strong>Workspace</strong>

              <span>
                Connected to FastAPI backend.
              </span>
            </div>

            <time>Now</time>
          </div>

          <div className="activity-item">
            <span className="activity-dot blue"></span>

            <div>
              <strong>Agents</strong>

              <span>
                {agents.length} agent
                {agents.length === 1
                  ? ''
                  : 's'} available.
              </span>
            </div>

            <time>Now</time>
          </div>

          <div className="activity-item">
            <span className="activity-dot purple"></span>

            <div>
              <strong>System</strong>

              <span>
                FastAPI, PostgreSQL and RAG are
                operational.
              </span>
            </div>

            <time>Today</time>
          </div>
        </div>
      </section>
    </div>
  )

  // --------------------------------------------------
  // Agents
  // --------------------------------------------------

  const renderAgents = () => (
    <div className="page-content">
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            WORKSPACE
          </p>

          <h1>AI Agents</h1>

          <p className="page-subtitle">
            Create, configure, and manage your
            digital employees.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={openCreateAgent}
        >
          + Create Agent
        </button>
      </div>

      {agents.length === 0 ? (
        <div className="panel empty-state">
          <h2>No agents yet</h2>

          <p>
            Create your first AI employee to get
            started.
          </p>

          <button
            className="primary-button"
            onClick={openCreateAgent}
          >
            + Create Agent
          </button>
        </div>
      ) : (
        <div className="agents-grid">
          {agents.map((agent) => (
            <div
              className="agent-card"
              key={agent.id}
            >
              <div className="agent-card-top">
                <div className="large-avatar">
                  AI
                </div>

                <span className="active-badge">
                  <i></i>
                  Active
                </span>
              </div>

              <h2>{agent.name}</h2>

              <p>{agent.description}</p>

              <div className="agent-meta">
                <span>Role</span>
                <strong>
                  {agent.role}
                </strong>

                <span>Model</span>
                <strong>
                  {agent.model}
                </strong>

                <span>Temperature</span>
                <strong>
                  {agent.temperature}
                </strong>
              </div>

              <button
                className="full-button"
                onClick={() => {
                  setSelectedAgent(agent)
                  setActivePage('chat')
                }}
              >
                Open Chat
              </button>
            </div>
          ))}

          <button
            className="new-agent-card"
            onClick={openCreateAgent}
          >
            <span>+</span>

            <strong>
              Create new agent
            </strong>

            <small>
              Configure a new digital employee
            </small>
          </button>
        </div>
      )}
    </div>
  )

  // --------------------------------------------------
  // Chat
  // --------------------------------------------------

  const renderChat = () => (
    <div className="page-content chat-page">
      <div className="page-heading compact">
        <div>
          <p className="eyebrow">
            AI CONVERSATION
          </p>

          <h1>
            {selectedAgent?.name ||
              'AI Agent'}
          </h1>

          <p className="page-subtitle">
            {selectedAgent?.description ||
              'Document-based AI assistant'}
          </p>
        </div>

        <span className="connection-badge">
          <i></i>
          Backend Ready
        </span>
      </div>

      <section className="chat-container">
        <div className="chat-header">
          <div className="agent-avatar">
            AI
          </div>

          <div>
            <strong>
              {selectedAgent?.name ||
                'AI Agent'}
            </strong>

            <span>
              Document-aware assistant
            </span>
          </div>
        </div>

        <div className="messages">
          {messages.length === 0 ? (
            <div className="empty-chat">
              <div className="empty-chat-icon">
                ✦
              </div>

              <h2>
                How can I help?
              </h2>

              <p>
                Ask questions about your
                uploaded documents or start a
                conversation with your agent.
              </p>

              <div className="suggestions">
                <button
                  onClick={() =>
                    setMessage(
                      'What is the special test value in the PROJECT-ATLAS document?',
                    )
                  }
                >
                  Ask about PROJECT-ATLAS
                </button>

                <button
                  onClick={() =>
                    setMessage(
                      'What is the project code name?',
                    )
                  }
                >
                  Ask about project code
                </button>
              </div>
            </div>
          ) : (
            messages.map((item, index) => (
              <div
                className={`message ${item.role}`}
                key={index}
              >
                <div className="message-avatar">
                  {item.role === 'user'
                    ? 'U'
                    : 'AI'}
                </div>

                <div className="message-bubble">
                  {item.content}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="chat-input-area">
          <textarea
            value={message}
            onChange={(event) =>
              setMessage(event.target.value)
            }
            onKeyDown={(event) => {
              if (
                event.key === 'Enter' &&
                !event.shiftKey
              ) {
                event.preventDefault()
                sendMessage()
              }
            }}
            placeholder="Message your AI agent..."
            rows="1"
            disabled={!selectedAgent}
          />

          <button
            className="send-button"
            onClick={sendMessage}
            disabled={
              !message.trim() ||
              !selectedAgent
            }
          >
            ↑
          </button>
        </div>

        <p className="input-hint">
          Press Enter to send • Shift + Enter
          for a new line
        </p>
      </section>
    </div>
  )

  // --------------------------------------------------
  // Documents
  // --------------------------------------------------

  const renderDocuments = () => (
    <div className="page-content">
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            KNOWLEDGE BASE
          </p>

          <h1>Documents</h1>

          <p className="page-subtitle">
            Upload documents and make them
            searchable by your AI agents.
          </p>
        </div>

        <button className="primary-button">
          + Upload Document
        </button>
      </div>

      <section className="upload-panel">
        <div className="upload-icon">
          ↑
        </div>

        <h2>
          Upload a document
        </h2>

        <p>
          PDF, DOCX, TXT and other supported
          formats can be indexed into the RAG
          knowledge base.
        </p>

        <button className="primary-button">
          Choose File
        </button>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>
              Indexed Documents
            </h2>

            <p>
              Documents currently available to
              the RAG system.
            </p>
          </div>
        </div>

        <div className="document-list">
          {[
            [
              'PROJECT-ATLAS',
              'api_rag_test.txt',
              '1 chunk',
            ],
            [
              'Loader Test',
              'loader_test.docx',
              '2 chunks',
            ],
            [
              'Loader Test',
              'loader_test.md',
              '1 chunk',
            ],
            [
              'Loader Test',
              'loader_test.txt',
              '1 chunk',
            ],
          ].map(
            ([title, filename, chunks]) => (
              <div
                className="document-row"
                key={filename}
              >
                <div className="document-icon">
                  ▣
                </div>

                <div>
                  <strong>
                    {title}
                  </strong>

                  <span>
                    {filename}
                  </span>
                </div>

                <span className="document-chunks">
                  {chunks}
                </span>

                <span className="indexed-badge">
                  Indexed
                </span>
              </div>
            ),
          )}
        </div>
      </section>
    </div>
  )

  // --------------------------------------------------
  // Conversations
  // --------------------------------------------------

  const renderConversations = () => (
    <div className="page-content">
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            HISTORY
          </p>

          <h1>
            Conversations
          </h1>

          <p className="page-subtitle">
            Review previous conversations
            with your AI agents.
          </p>
        </div>
      </div>

      <section className="panel">
        <div className="conversation-row">
          <div className="conversation-icon">
            ◉
          </div>

          <div className="conversation-info">
            <strong>
              What is the special test value in
              the PROJECT-ATLAS...
            </strong>

            <span>
              RAG Test Agent • The special test
              value is ATLAS-9472.
            </span>
          </div>

          <time>
            Today
          </time>
        </div>

        <div className="conversation-row">
          <div className="conversation-icon">
            ◉
          </div>

          <div className="conversation-info">
            <strong>
              What is the project code name?
            </strong>

            <span>
              RAG Test Agent •
              PROJECT-ATLAS-2026.
            </span>
          </div>

          <time>
            Today
          </time>
        </div>
      </section>
    </div>
  )

  // --------------------------------------------------
  // Page Router
  // --------------------------------------------------

  const renderPage = () => {
    switch (activePage) {
      case 'agents':
        return renderAgents()

      case 'chat':
        return renderChat()

      case 'documents':
        return renderDocuments()

      case 'conversations':
        return renderConversations()

      default:
        return renderDashboard()
    }
  }

  // --------------------------------------------------
  // Main Application
  // --------------------------------------------------

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            D
          </div>

          <div>
            <strong>DigiEmp</strong>
            <span>
              AI Agent Platform
            </span>
          </div>
        </div>

        <div className="workspace-label">
          WORKSPACE
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={
                activePage === item.id
                  ? 'nav-item active'
                  : 'nav-item'
              }
              onClick={() =>
                setActivePage(item.id)
              }
            >
              <span className="nav-icon">
                {item.icon}
              </span>

              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-spacer"></div>

        <div className="system-card">
          <div className="system-card-title">
            <span className="online-dot"></span>
            System Online
          </div>

          <span>
            FastAPI • PostgreSQL • RAG
          </span>
        </div>

        <button
          className="user-card"
          onClick={logout}
        >
          <div className="user-avatar">
            {currentUser?.username
              ?.charAt(0)
              .toUpperCase() || 'U'}
          </div>

          <div>
            <strong>
              {currentUser?.username ||
                'User'}
            </strong>

            <span>
              Click to logout
            </span>
          </div>

          <span className="more-icon">
            ⋮
          </span>
        </button>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            DigiEmp <span>/</span>{' '}
            {
              navItems.find(
                (item) =>
                  item.id === activePage,
              )?.label
            }
          </div>

          <div className="topbar-actions">
            <button
              className="icon-button"
              title="Notifications"
            >
              ♢
            </button>

            <button
              className="help-button"
              title="Help"
            >
              ?
            </button>
          </div>
        </header>

        {loginError && (
          <div className="api-error">
            {loginError}
          </div>
        )}

        {renderPage()}
      </main>

      {/* --------------------------------------------------
          Create Agent Modal
          -------------------------------------------------- */}

      {showCreateAgent && (
        <div
          className="modal-overlay"
          onMouseDown={(event) => {
            if (
              event.target ===
              event.currentTarget
            ) {
              closeCreateAgent()
            }
          }}
        >
          <div
            className="modal-card"
            onMouseDown={(event) =>
              event.stopPropagation()
            }
          >
            <div className="modal-header">
              <div>
                <p className="eyebrow">
                  NEW DIGITAL EMPLOYEE
                </p>

                <h2>
                  Create AI Agent
                </h2>

                <p>
                  Configure an AI employee and
                  connect it to your workspace.
                </p>
              </div>

              <button
                className="modal-close"
                onClick={closeCreateAgent}
                disabled={creatingAgent}
              >
                ×
              </button>
            </div>

            <form
              className="agent-form"
              onSubmit={createAgent}
            >
              <div className="form-grid">
                <label>
                  Agent Name
                  <input
                    name="name"
                    value={agentForm.name}
                    onChange={
                      handleAgentFormChange
                    }
                    placeholder="e.g. Research Assistant"
                    autoFocus
                  />
                </label>

                <label>
                  Role
                  <input
                    name="role"
                    value={agentForm.role}
                    onChange={
                      handleAgentFormChange
                    }
                    placeholder="assistant"
                  />
                </label>
              </div>

              <label>
                Description
                <input
                  name="description"
                  value={
                    agentForm.description
                  }
                  onChange={
                    handleAgentFormChange
                  }
                  placeholder="What is this agent responsible for?"
                />
              </label>

              <label>
                System Prompt
                <textarea
                  name="system_prompt"
                  value={
                    agentForm.system_prompt
                  }
                  onChange={
                    handleAgentFormChange
                  }
                  rows="4"
                  placeholder="Describe how the agent should behave..."
                />
              </label>

              <div className="form-grid">
                <label>
                  Model
                  <input
                    name="model"
                    value={agentForm.model}
                    onChange={
                      handleAgentFormChange
                    }
                    placeholder="qwen2.5:3b"
                  />
                </label>

                <label>
                  Temperature
                  <input
                    type="number"
                    name="temperature"
                    value={
                      agentForm.temperature
                    }
                    onChange={
                      handleAgentFormChange
                    }
                    min="0"
                    max="2"
                    step="0.1"
                  />
                </label>
              </div>

              {createAgentError && (
                <div className="login-error">
                  {createAgentError}
                </div>
              )}

              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={closeCreateAgent}
                  disabled={creatingAgent}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={creatingAgent}
                >
                  {creatingAgent
                    ? 'Creating...'
                    : 'Create Agent'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default App