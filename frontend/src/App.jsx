import React, { useState, useEffect, useRef } from 'react'
import {
  Code2,
  Shield,
  Layers,
  FileText,
  HelpCircle,
  MessageSquare,
  Search,
  Plus,
  Loader,
  AlertTriangle,
  FolderOpen,
  ArrowRight,
  Database,
  Globe,
  Terminal,
  ChevronRight,
  ChevronDown,
  FileCode,
  Folder,
  Send,
  User,
  Bot,
  Copy,
  Check,
  Calendar,
  Trash2
} from 'lucide-react'

const API_BASE = ""

function parseInlineMarkdown(text) {
  if (!text) return "";
  
  let parts = [text];
  
  parts = parts.flatMap(p => {
    if (typeof p !== 'string') return p;
    const split = p.split(/(`[^`]+`)/g);
    return split.map((part, i) => {
      if (part.startsWith("`") && part.endsWith("`")) {
        return (
          <code key={i} className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-850 font-mono text-[10px] text-indigo-300 mx-0.5">
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  });
  
  parts = parts.flatMap(p => {
    if (typeof p !== 'string' && !React.isValidElement(p)) return p;
    if (typeof p !== 'string') return [p];
    const split = p.split(/(\*\*[^*]+\*\*)/g);
    return split.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={i} className="font-extrabold text-slate-100">{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  });

  parts = parts.flatMap(p => {
    if (typeof p !== 'string' && !React.isValidElement(p)) return p;
    if (typeof p !== 'string') return [p];
    const split = p.split(/(\*[^*]+\*)/g);
    return split.map((part, i) => {
      if (part.startsWith("*") && part.endsWith("*")) {
        return <em key={i} className="italic text-slate-400">{part.slice(1, -1)}</em>;
      }
      return part;
    });
  });
  
  return parts;
}

function MarkdownRenderer({ content }) {
  if (!content) return null;
  
  const parts = content.split(/(```[\s\S]*?```)/g);
  
  return (
    <div className="space-y-2 markdown-content text-xs leading-relaxed text-slate-300">
      {parts.map((part, index) => {
        if (part.startsWith("```")) {
          const lines = part.split("\n");
          const firstLine = lines[0] || "";
          const language = firstLine.replace("```", "").trim() || "code";
          const code = lines.slice(1, -1).join("\n");
          return (
            <div key={index} className="my-3 rounded-xl overflow-hidden border border-slate-900 bg-slate-950 font-mono shadow-inner">
              <div className="flex items-center justify-between px-4 py-2 bg-slate-900/60 border-b border-slate-900 text-[10px] text-slate-500 font-bold uppercase tracking-wider select-none">
                <span>{language}</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigator.clipboard.writeText(code);
                  }}
                  className="hover:text-indigo-400 flex items-center gap-1 transition-colors"
                >
                  <Copy className="w-3 h-3" /> Copy
                </button>
              </div>
              <pre className="p-4 overflow-x-auto text-[11px] text-slate-350 custom-scrollbar">{code}</pre>
            </div>
          );
        } else {
          const lines = part.split("\n");
          return (
            <div key={index} className="space-y-1">
              {lines.map((line, lineIdx) => {
                const trimmed = line.trim();
                
                if (trimmed.startsWith("#")) {
                  const level = (trimmed.match(/^#+/) || ["#"])[0].length;
                  const text = trimmed.replace(/^#+\s*/, "");
                  const sizeClass = 
                    level === 1 ? "text-base font-extrabold text-white mt-4 mb-2 font-display uppercase tracking-wide border-b border-slate-900 pb-1" :
                    level === 2 ? "text-sm font-bold text-slate-100 mt-3 mb-1.5 font-display border-b border-slate-900/50 pb-0.5" :
                    "text-xs font-bold text-slate-200 mt-2.5 mb-1 tracking-wide";
                  return <div key={lineIdx} className={sizeClass}>{parseInlineMarkdown(text)}</div>;
                }
                
                if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
                  const text = trimmed.substring(2);
                  return (
                    <ul key={lineIdx} className="list-disc pl-5 my-0.5 space-y-0.5 text-slate-300">
                      <li>{parseInlineMarkdown(text)}</li>
                    </ul>
                  );
                }

                if (/^\d+\.\s+/.test(trimmed)) {
                  const match = trimmed.match(/^(\d+\.)\s+(.*)/);
                  if (match) {
                    return (
                      <ol key={lineIdx} className="list-decimal pl-5 my-0.5 space-y-0.5 text-slate-300">
                        <li>{parseInlineMarkdown(match[2])}</li>
                      </ol>
                    );
                  }
                }
                
                if (trimmed.startsWith("> ")) {
                  const text = trimmed.substring(2);
                  return (
                    <blockquote key={lineIdx} className="border-l-2 border-indigo-500 bg-indigo-500/5 px-3 py-1.5 my-1.5 rounded-r-lg text-slate-400 italic">
                      {parseInlineMarkdown(text)}
                    </blockquote>
                  );
                }
                
                if (trimmed === "---" || trimmed === "***") {
                  return <hr key={lineIdx} className="border-slate-900 my-3" />;
                }
                
                if (trimmed === "") {
                  return <div key={lineIdx} className="h-1" />;
                }
                
                return <p key={lineIdx} className="text-slate-300 mb-0.5 leading-relaxed">{parseInlineMarkdown(line)}</p>;
              })}
            </div>
          );
        }
      })}
    </div>
  );
}

export default function App() {
  const [repoUrl, setRepoUrl] = useState("")
  const [activeTab, setActiveTab] = useState("analysis") // analysis, stack_arch, security, docs, interview
  const [docSubTab, setDocSubTab] = useState("readme") // readme, architecture, api_reference, onboarding
  const [interviewSubTab, setInterviewSubTab] = useState("beginner") // beginner, intermediate, advanced, system_design
  
  const [analysesList, setAnalysesList] = useState([])
  const [selectedAnalysisId, setSelectedAnalysisId] = useState(null)
  const [currentAnalysis, setCurrentAnalysis] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [triggerPoll, setTriggerPoll] = useState(0)

  // Chat states
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState("")
  const [isSendingChat, setIsSendingChat] = useState(false)
  const chatEndRef = useRef(null)

  // Expanded tree nodes and interview question indices
  const [expandedNodes, setExpandedNodes] = useState({})
  const [expandedQuestions, setExpandedQuestions] = useState({})
  const [copiedDoc, setCopiedDoc] = useState(false)

  const [securityFilter, setSecurityFilter] = useState(null)
  const [isOnline, setIsOnline] = useState(true)

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_BASE}/`)
        if (res.ok) {
          setIsOnline(true)
        } else {
          setIsOnline(false)
        }
      } catch (err) {
        setIsOnline(false)
      }
    }
    checkStatus()
    const interval = setInterval(checkStatus, 15000)
    return () => clearInterval(interval)
  }, [])

  const handleDeleteAnalysis = (e, idToDelete) => {
    e.stopPropagation()
    const updated = analysesList.filter(a => a.id !== idToDelete)
    setAnalysesList(updated)
    localStorage.setItem("copilot_analyses_ids", JSON.stringify(updated))
    if (selectedAnalysisId === idToDelete) {
      if (updated.length > 0) {
        setSelectedAnalysisId(updated[0].id)
      } else {
        setSelectedAnalysisId(null)
        setCurrentAnalysis(null)
      }
    }
  }

  // Load history from local storage
  useEffect(() => {
    const stored = localStorage.getItem("copilot_analyses_ids")
    if (stored) {
      const ids = JSON.parse(stored)
      setAnalysesList(ids)
      if (ids.length > 0 && !selectedAnalysisId) {
        setSelectedAnalysisId(ids[0].id)
      }
    }
  }, [])

  // Poll analysis state
  useEffect(() => {
    if (!selectedAnalysisId) return
    
    let isMounted = true
    const fetchAnalysis = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/analysis/${selectedAnalysisId}`)
        if (res.ok) {
          const data = await res.json()
          if (isMounted) {
            setCurrentAnalysis(data)
            // If pending/analyzing, poll again in 4 seconds
            if (data.status === "pending" || data.status === "analyzing" || data.status === "cloning") {
              setTimeout(() => setTriggerPoll(p => p + 1), 4000)
            }
          }
        }
      } catch (err) {
        console.error("Error fetching analysis details:", err)
      }
    }

    fetchAnalysis()
    
    // Fetch chat history
    const fetchChatHistory = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/analysis/${selectedAnalysisId}/chat/history`)
        if (res.ok) {
          const data = await res.json()
          if (isMounted) {
            setChatMessages(data.map(m => ({
              id: m.id,
              sender: m.sender,
              message: m.message,
              sources: m.sources || []
            })))
          }
        }
      } catch (err) {
        console.error("Error fetching chat history:", err)
      }
    }
    fetchChatHistory()

    return () => {
      isMounted = false
    }
  }, [selectedAnalysisId, triggerPoll])

  // Scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  const handleStartAnalysis = async (e) => {
    e.preventDefault()
    if (!repoUrl.trim()) return
    
    setIsSubmitting(true)
    try {
      const res = await fetch(`${API_BASE}/api/analyze-repository`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl })
      })
      
      if (res.ok) {
        const newAnalysis = await res.json()
        const updatedList = [
          { id: newAnalysis.id, repo_url: newAnalysis.repo_url, repo_name: repoUrl.split("/").pop().replace(".git", ""), date: new Date().toLocaleDateString() },
          ...analysesList
        ]
        setAnalysesList(updatedList)
        localStorage.setItem("copilot_analyses_ids", JSON.stringify(updatedList))
        setSelectedAnalysisId(newAnalysis.id)
        setCurrentAnalysis(newAnalysis)
        setRepoUrl("")
        setActiveTab("analysis")
      } else {
        alert("Failed to queue analysis. Ensure URL is correct.")
      }
    } catch (err) {
      console.error(err)
      alert("Error sending request to server.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSendChat = async (e) => {
    e.preventDefault()
    if (!chatInput.trim() || isSendingChat || !selectedAnalysisId) return

    const userMsg = { id: String(Date.now()), sender: "user", message: chatInput, sources: [] }
    setChatMessages(prev => [...prev, userMsg])
    setChatInput("")
    setIsSendingChat(true)

    try {
      const res = await fetch(`${API_BASE}/api/analysis/${selectedAnalysisId}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.message })
      })
      if (res.ok) {
        const replyData = await res.json()
        setChatMessages(prev => [...prev, {
          id: String(Date.now() + 1),
          sender: "assistant",
          message: replyData.reply,
          sources: replyData.sources || []
        }])
      } else {
        setChatMessages(prev => [...prev, {
          id: String(Date.now() + 1),
          sender: "assistant",
          message: "Sorry, I had trouble answering that query. Ensure Ollama service is connected.",
          sources: []
        }])
      }
    } catch (err) {
      console.error(err)
    } finally {
      setIsSendingChat(false)
    }
  }

  const toggleNode = (nodePath) => {
    setExpandedNodes(prev => ({
      ...prev,
      [nodePath]: !prev[nodePath]
    }))
  }

  const toggleQuestion = (idx) => {
    setExpandedQuestions(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }))
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    setCopiedDoc(true)
    setTimeout(() => setCopiedDoc(false), 2000)
  }

  const renderTree = (node) => {
    if (!node) return null
    const isDir = node.type === "directory"
    const isExpanded = expandedNodes[node.path]
    
    return (
      <div key={node.path} className="pl-3">
        <div 
          onClick={() => isDir && toggleNode(node.path)}
          className={`flex items-center space-x-2 py-1 px-2 rounded cursor-pointer transition-colors ${
            isDir ? "hover:bg-slate-900/60 font-semibold" : "hover:bg-slate-900/40 text-slate-350"
          }`}
        >
          {isDir ? (
            <>
              {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-500" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
              <Folder className="w-4 h-4 text-indigo-450 fill-indigo-450/15" />
              <span className="text-xs text-slate-200">{node.name}</span>
            </>
          ) : (
            <>
              <div className="w-4"></div>
              <FileCode className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-xs text-slate-350">{node.name}</span>
              {node.size && <span className="text-[10px] text-slate-650">({(node.size / 1024).toFixed(1)} KB)</span>}
            </>
          )}
        </div>
        
        {isDir && isExpanded && node.children && (
          <div className="border-l border-slate-900 ml-3.5 mt-0.5 pl-0.5">
            {node.children.map(child => renderTree(child))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950 text-slate-100 font-sans select-none">
      
      {/* Background gradients */}
      <div className="absolute top-0 left-1/4 w-[450px] h-[450px] bg-indigo-600/5 rounded-full blur-[140px] pointer-events-none animate-pulse-slow"></div>
      <div className="absolute bottom-10 right-1/4 w-[450px] h-[450px] bg-violet-600/5 rounded-full blur-[140px] pointer-events-none animate-pulse-slow"></div>

      {/* Sidebar */}
      <aside className="w-64 glass-panel border-r border-slate-900 flex flex-col z-20">
        <div className="p-5 border-b border-slate-900 flex items-center space-x-3.5">
          <div className="w-9 h-9 bg-gradient-to-tr from-indigo-650 to-violet-650 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-650/20 border border-indigo-500/30">
            <Code2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-extrabold text-sm tracking-wide text-white font-display uppercase">AI Copilot</h1>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">Engineering Assistant</p>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto custom-scrollbar select-none">
          <button 
            onClick={() => setActiveTab("analysis")} 
            className={`w-full flex items-center space-x-3.5 px-4 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all ${
              activeTab === "analysis" 
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/15" 
                : "text-slate-400 hover:bg-slate-900/50 hover:text-slate-200"
            }`}
          >
            <Search className="w-4 h-4" />
            <span>Repository Analyzer</span>
          </button>
          
          <button 
            onClick={() => setActiveTab("stack_arch")} 
            disabled={!currentAnalysis || currentAnalysis.status !== "completed"}
            className={`w-full flex items-center space-x-3.5 px-4 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all ${
              !currentAnalysis || currentAnalysis.status !== "completed" ? "opacity-40 cursor-not-allowed" : ""
            } ${
              activeTab === "stack_arch" 
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/15" 
                : "text-slate-400 hover:bg-slate-900/50 hover:text-slate-200"
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Stack & Architecture</span>
          </button>

          <button 
            onClick={() => setActiveTab("security")} 
            disabled={!currentAnalysis || currentAnalysis.status !== "completed"}
            className={`w-full flex items-center space-x-3.5 px-4 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all ${
              !currentAnalysis || currentAnalysis.status !== "completed" ? "opacity-40 cursor-not-allowed" : ""
            } ${
              activeTab === "security" 
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/15" 
                : "text-slate-400 hover:bg-slate-900/50 hover:text-slate-200"
            }`}
          >
            <Shield className="w-4 h-4" />
            <span>Security Audits</span>
          </button>

          <button 
            onClick={() => setActiveTab("docs")} 
            disabled={!currentAnalysis || currentAnalysis.status !== "completed"}
            className={`w-full flex items-center space-x-3.5 px-4 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all ${
              !currentAnalysis || currentAnalysis.status !== "completed" ? "opacity-40 cursor-not-allowed" : ""
            } ${
              activeTab === "docs" 
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/15" 
                : "text-slate-400 hover:bg-slate-900/50 hover:text-slate-200"
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Documentation</span>
          </button>

          <button 
            onClick={() => setActiveTab("interview")} 
            disabled={!currentAnalysis || currentAnalysis.status !== "completed"}
            className={`w-full flex items-center space-x-3.5 px-4 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all ${
              !currentAnalysis || currentAnalysis.status !== "completed" ? "opacity-40 cursor-not-allowed" : ""
            } ${
              activeTab === "interview" 
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/15" 
                : "text-slate-400 hover:bg-slate-900/50 hover:text-slate-200"
            }`}
          >
            <HelpCircle className="w-4 h-4" />
            <span>Interview Preparation</span>
          </button>

          <div className="pt-6 border-t border-slate-900 my-4 select-none">
            <h2 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-4 mb-3">Previous Scans</h2>
            <div className="space-y-2 px-3 overflow-y-auto max-h-[300px] custom-scrollbar">
              {analysesList.map(a => (
                <div
                  key={a.id}
                  onClick={() => setSelectedAnalysisId(a.id)}
                  className={`group relative p-3 rounded-xl border cursor-pointer transition-all ${
                    selectedAnalysisId === a.id 
                      ? "bg-slate-900/80 border-indigo-500/80 shadow-md shadow-indigo-650/5 text-indigo-400" 
                      : "bg-slate-950/45 border-slate-900/60 text-slate-400 hover:bg-slate-900/30 hover:border-slate-800 hover:text-slate-200"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center space-x-2 truncate">
                      <Folder className="w-3.5 h-3.5 flex-shrink-0 text-slate-500 group-hover:text-indigo-400 transition-colors" />
                      <span className="text-xs font-bold truncate tracking-wide">{a.repo_name}</span>
                    </div>
                    
                    <button
                      type="button"
                      onClick={(e) => handleDeleteAnalysis(e, a.id)}
                      className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-slate-850 rounded text-slate-500 hover:text-red-400 transition-all flex-shrink-0"
                      title="Delete History"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  
                  <div className="mt-2 flex items-center justify-between text-[9px] text-slate-550 font-mono">
                    <span className="flex items-center gap-1 font-medium uppercase tracking-wider">
                      <Calendar className="w-2.5 h-2.5 text-slate-650" />
                      {a.date || "recent"}
                    </span>
                    {a.id && (
                      <span className="bg-slate-950/50 px-1.5 py-0.5 rounded border border-slate-900 text-slate-600">
                        {a.id.substring(0, 6)}
                      </span>
                    )}
                  </div>
                </div>
              ))}
              {analysesList.length === 0 && (
                <span className="text-[11px] text-slate-600 px-4 block italic">No scans recorded.</span>
              )}
            </div>
          </div>
        </nav>
      </aside>

      {/* Main content viewport */}
      <main className="flex-1 flex flex-col overflow-hidden z-10 bg-slate-950/20 backdrop-blur-3xl">
        
        {/* Topheader */}
        <header className="h-16 border-b border-slate-900 flex items-center justify-between px-8 bg-slate-950/50 backdrop-blur-md z-10">
          <div className="flex items-center space-x-3.5">
            <h2 className="text-base font-extrabold text-white tracking-wide font-display">
              {currentAnalysis ? currentAnalysis.repo_name || "Cloning repository..." : "Select Workspace"}
            </h2>
            {currentAnalysis && (
              <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider ${
                currentAnalysis.status === "completed" 
                  ? "bg-emerald-500/10 text-emerald-450 border border-emerald-500/20" 
                  : currentAnalysis.status === "failed"
                  ? "bg-red-500/10 text-red-450 border border-red-500/20"
                  : "bg-indigo-500/10 text-indigo-455 border border-indigo-500/20 animate-pulse"
              }`}>
                {currentAnalysis.status}
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-3">
            {/* API Health Pill */}
            <div className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border select-none transition-all ${
              isOnline 
                ? "bg-emerald-500/5 text-emerald-450 border-emerald-500/10" 
                : "bg-rose-500/5 text-rose-450 border-rose-500/10"
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${isOnline ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`} />
              <span>{isOnline ? "API Online" : "API Offline"}</span>
            </div>

            {/* Model Pill */}
            <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold text-indigo-400 bg-indigo-500/5 border border-indigo-500/10 select-none">
              <Bot className="w-3 h-3 text-indigo-400" />
              <span>qwen2.5-coder:3b</span>
            </div>

            {currentAnalysis?.commit_hash && (
              <div className="text-[10px] text-slate-455 font-mono bg-slate-900/50 px-3 py-1 rounded-lg border border-slate-900">
                commit: <span className="text-slate-300">{currentAnalysis.commit_hash.substring(0, 8)}</span>
              </div>
            )}
          </div>
        </header>

        {/* Content body container */}
        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
          
          {/* TAB: Analysis */}
          {activeTab === "analysis" && (
            <div className="space-y-6">
              
              {/* Form submit widget */}
              <div className="glass-panel p-6 rounded-2xl border border-slate-900 shadow-xl">
                <h3 className="text-sm font-extrabold text-white uppercase tracking-wider mb-1">Analyze Git Repository</h3>
                <p className="text-[11px] text-slate-450 mb-4">Input a public URL below to kick off stack identification, static security auditing, and vector RAG indexing.</p>
                <form onSubmit={handleStartAnalysis} className="flex gap-3">
                  <div className="relative flex-1">
                    <Search className="absolute left-3.5 top-3.5 text-slate-500 w-4 h-4" />
                    <input 
                      type="url"
                      placeholder="https://github.com/fastapi/fastapi"
                      value={repoUrl}
                      onChange={(e) => setRepoUrl(e.target.value)}
                      className="w-full bg-slate-950/80 border border-slate-900 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-200 placeholder-slate-650 focus:outline-none focus:border-indigo-500 transition-colors"
                      required
                    />
                  </div>
                  <button 
                    type="submit"
                    disabled={isSubmitting}
                    className="bg-indigo-600 hover:bg-indigo-550 text-white px-5 rounded-xl text-xs font-bold tracking-wider flex items-center space-x-2 transition-colors disabled:opacity-50"
                  >
                    {isSubmitting ? <Loader className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                    <span>{isSubmitting ? "Queueing..." : "Scan Repo"}</span>
                  </button>
                </form>
              </div>

              {/* ProgressTimeline */}
              {currentAnalysis && currentAnalysis.status !== "completed" && currentAnalysis.status !== "failed" && (
                <div className="glass-panel p-6 rounded-2xl border border-slate-900 space-y-4">
                  <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-widest flex items-center space-x-2">
                    <Loader className="w-3.5 h-3.5 animate-spin" />
                    <span>Analysis Agent Execution Tracker</span>
                  </h3>
                  
                  <div className="relative pl-6 border-l border-slate-900 space-y-6">
                    <div className="relative">
                      <div className={`absolute -left-[30px] w-4.5 h-4.5 rounded-full border-2 flex items-center justify-center text-[8px] font-bold ${
                        ["pending", "analyzing", "cloning", "indexing", "completed"].includes(currentAnalysis.status)
                          ? "bg-indigo-600 border-indigo-500 text-white" : "bg-slate-950 border-slate-900"
                      }`}>✓</div>
                      <h4 className="text-xs font-bold text-slate-200">Repository Clone & Mapped file tree</h4>
                      <p className="text-[10px] text-slate-500">Retrieving code structure via GitPython.</p>
                    </div>

                    <div className="relative">
                      <div className={`absolute -left-[30px] w-4.5 h-4.5 rounded-full border-2 flex items-center justify-center text-[8px] font-bold ${
                        currentAnalysis.status === "analyzing" || currentAnalysis.status === "indexing" || currentAnalysis.status === "completed"
                          ? "bg-indigo-600 border-indigo-500 text-white animate-pulse" : "bg-slate-950 border-slate-900"
                      }`}>2</div>
                      <h4 className="text-xs font-bold text-slate-200">Agent Network Review</h4>
                      <p className="text-[10px] text-slate-500">Tech Stack Detection $\rightarrow$ Architecture Audit $\rightarrow$ Security scan $\rightarrow$ Complexity evaluation.</p>
                    </div>

                    <div className="relative">
                      <div className={`absolute -left-[30px] w-4.5 h-4.5 rounded-full border-2 flex items-center justify-center text-[8px] font-bold ${
                        currentAnalysis.status === "indexing" || currentAnalysis.status === "completed"
                          ? "bg-indigo-600 border-indigo-500 text-white" : "bg-slate-950 border-slate-900"
                      }`}>3</div>
                      <h4 className="text-xs font-bold text-slate-200">Vector Storage Indexing</h4>
                      <p className="text-[10px] text-slate-500">Creating embeddings with BAAI/bge-small-en-v1.5 and storage with FAISS.</p>
                    </div>
                  </div>
                </div>
              )}

              {currentAnalysis && currentAnalysis.status === "failed" && (
                <div className="bg-red-950/10 border border-red-900/20 p-6 rounded-2xl text-slate-300 space-y-2">
                  <div className="flex items-center space-x-2 text-red-400 font-bold text-xs uppercase tracking-wider">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Pipeline Failed</span>
                  </div>
                  <p className="text-xs text-slate-500 font-mono bg-slate-950 p-4 rounded-xl border border-red-950/20">
                    {currentAnalysis.error_message || "Process execution exception occurred."}
                  </p>
                </div>
              )}

              {/* Summary Card and Health Score */}
              {currentAnalysis && currentAnalysis.status === "completed" && (
                <div className="glass-panel p-6 rounded-2xl border border-slate-900 shadow-xl bg-slate-950/40 backdrop-blur-md grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                  <div className="flex flex-col items-center justify-center p-4 border-b md:border-b-0 md:border-r border-slate-900">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">Repository Health Score</span>
                    <div className="relative flex items-center justify-center">
                      {/* Big Circle Score */}
                      <svg className="w-24 h-24 transform -rotate-90">
                        <circle cx="48" cy="48" r="40" stroke="#090d16" strokeWidth="8" fill="transparent" />
                        <circle cx="48" cy="48" r="40" stroke="#6366f1" strokeWidth="8" fill="transparent"
                          strokeDasharray={2 * Math.PI * 40}
                          strokeDashoffset={2 * Math.PI * 40 * (1 - (currentAnalysis.code_quality?.code_quality_score || 87) / 100)}
                          strokeLinecap="round"
                          className="transition-all duration-1000"
                        />
                      </svg>
                      <div className="absolute text-center">
                        <span className="text-2xl font-black text-white">{currentAnalysis.code_quality?.code_quality_score || 87}</span>
                        <span className="text-[10px] text-slate-500 block">/ 100</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="md:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-y-3 gap-x-6 p-2">
                    <div className="flex items-center space-x-3 text-slate-200">
                      <div className="w-5 h-5 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 text-xs font-bold font-sans">✓</div>
                      <span className="text-xs font-semibold">Tech Stack Detected</span>
                    </div>
                    <div className="flex items-center space-x-3 text-slate-200">
                      <div className="w-5 h-5 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 text-xs font-bold font-sans">✓</div>
                      <span className="text-xs font-semibold">Architecture Mapped</span>
                    </div>
                    <div className="flex items-center space-x-3 text-slate-200">
                      <div className="w-5 h-5 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 text-xs font-bold font-sans">✓</div>
                      <span className="text-xs font-semibold">Security Scan Completed</span>
                    </div>
                    <div className="flex items-center space-x-3 text-slate-200">
                      <div className="w-5 h-5 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 text-xs font-bold font-sans">✓</div>
                      <span className="text-xs font-semibold">Complexity Analysis</span>
                    </div>
                    <div className="flex items-center space-x-3 text-slate-200">
                      <div className="w-5 h-5 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 text-xs font-bold font-sans">✓</div>
                      <span className="text-xs font-semibold">Documentation Generated</span>
                    </div>
                    <div className="flex items-center space-x-3 text-slate-200">
                      <div className="w-5 h-5 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 text-xs font-bold font-sans">✓</div>
                      <span className="text-xs font-semibold">RAG Index Ready</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Mapped view layout */}
              {currentAnalysis && currentAnalysis.status === "completed" && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  
                  {/* Tree explorer */}
                  <div className="glass-panel p-5 rounded-2xl border border-slate-900 flex flex-col h-[500px]">
                    <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3.5 flex items-center space-x-2 border-b border-slate-900 pb-2">
                      <FolderOpen className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Codebase File tree</span>
                    </h3>
                    
                    <div className="flex-1 overflow-y-auto custom-scrollbar bg-slate-950/40 p-3 rounded-xl border border-slate-900">
                      {currentAnalysis.tree_structure ? renderTree(currentAnalysis.tree_structure) : (
                        <p className="text-xs text-slate-500 italic p-4">No structure mapped.</p>
                      )}
                    </div>
                  </div>

                  {/* Q&A Chat widget */}
                  <div className="lg:col-span-2 glass-panel rounded-2xl border border-slate-900 flex flex-col h-[500px] overflow-hidden">
                    <div className="p-4 border-b border-slate-900 bg-slate-950/50 flex items-center space-x-2">
                      <MessageSquare className="w-4 h-4 text-indigo-400" />
                      <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Q&A Chat Assistant</h3>
                    </div>

                    <div className="flex-1 overflow-y-auto p-5 space-y-4 custom-scrollbar bg-slate-950/25">
                      {chatMessages.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-full text-slate-500 text-center px-6">
                          <Bot className="w-9 h-9 text-slate-750 mb-2" />
                          <p className="text-xs font-semibold text-slate-400">Copilot Chat Bot</p>
                          <p className="text-[10px] text-slate-600 mt-1 max-w-xs leading-relaxed">Ask detailed queries regarding directory maps, component files, or logic structure.</p>
                        </div>
                      )}
                      
                      {chatMessages.map((msg) => (
                        <div key={msg.id} className={`flex space-x-3.5 ${msg.sender === "user" ? "justify-end" : ""}`}>
                          {msg.sender !== "user" && (
                            <div className="relative w-7 h-7 rounded-lg bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 flex-shrink-0 select-none">
                              <Bot className="w-4 h-4" />
                              <span className="absolute bottom-0 right-0 w-1.5 h-1.5 bg-emerald-500 rounded-full border border-slate-950 animate-pulse" />
                            </div>
                          )}
                          
                          <div className={`p-3.5 rounded-2xl max-w-[85%] text-xs shadow-md ${
                            msg.sender === "user" 
                              ? "bg-indigo-650 text-white rounded-tr-none" 
                              : "bg-slate-900 text-slate-200 border border-slate-850/80 rounded-tl-none leading-relaxed"
                          }`}>
                            <MarkdownRenderer content={msg.message} />
                            
                            {msg.sender !== "user" && msg.sources && msg.sources.length > 0 && (
                              <div className="mt-3.5 pt-2.5 border-t border-slate-850 space-y-1.5">
                                <span className="text-[9px] font-bold text-slate-500 block uppercase tracking-wider">Sources:</span>
                                <div className="flex flex-wrap gap-1">
                                  {msg.sources.map((s, idx) => (
                                    <span key={idx} className="bg-slate-950/60 text-slate-400 px-2 py-0.5 rounded border border-slate-850 font-mono text-[9px] truncate max-w-[200px]" title={s.file}>
                                      {s.file.split("/").pop()}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                          
                          {msg.sender === "user" && (
                            <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-350 flex-shrink-0">
                              <User className="w-4 h-4" />
                            </div>
                          )}
                        </div>
                      ))}
                      
                      {isSendingChat && (
                        <div className="flex space-x-3.5">
                          <div className="relative w-7 h-7 rounded-lg bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 flex-shrink-0 select-none">
                            <Bot className="w-4 h-4" />
                            <span className="absolute bottom-0 right-0 w-1.5 h-1.5 bg-indigo-500 rounded-full border border-slate-950 animate-ping" />
                          </div>
                          <div className="bg-slate-900 border border-slate-850/60 p-3 rounded-2xl rounded-tl-none">
                            <Loader className="w-3.5 h-3.5 text-indigo-400 animate-spin" />
                          </div>
                        </div>
                      )}
                      
                      <div ref={chatEndRef} />
                    </div>

                    {/* Chat Prompt Suggestions */}
                    <div className="px-4 py-2 border-t border-slate-900/60 bg-slate-950/40 flex flex-wrap gap-2 select-none">
                      {[
                        "What frameworks are used here?",
                        "Identify security flaws in this repo",
                        "Give an onboarding layout structure"
                      ].map((promptText, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => {
                            setChatInput(promptText);
                          }}
                          className="bg-slate-900/60 hover:bg-slate-900 border border-slate-850 hover:border-indigo-500/30 text-[10px] font-semibold text-slate-400 hover:text-indigo-400 px-2.5 py-1 rounded-lg transition-all"
                        >
                          {promptText}
                        </button>
                      ))}
                    </div>

                    <form onSubmit={handleSendChat} className="p-3 border-t border-slate-900 bg-slate-950/50 flex gap-2">
                      <input 
                        type="text"
                        placeholder="Ask how database pooling is managed or where files are stored..."
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        className="flex-1 bg-slate-900 border border-slate-850/80 text-xs text-slate-200 px-4 py-2.5 rounded-xl placeholder-slate-550 focus:outline-none focus:border-indigo-500 transition-colors"
                      />
                      <button 
                        type="submit"
                        disabled={isSendingChat || !chatInput.trim()}
                        className="bg-indigo-650 hover:bg-indigo-600 disabled:opacity-50 text-white w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </form>
                  </div>

                </div>
              )}

              {!currentAnalysis && (
                <div className="flex flex-col items-center justify-center py-20 text-slate-500">
                  <Code2 className="w-12 h-12 text-slate-850 mb-3" />
                  <p className="text-xs font-bold text-slate-400">No Active analysis record</p>
                  <p className="text-[10px] text-slate-600 text-center max-w-sm mt-1">Submit a GitHub URL above to retrieve structured metadata and start analysis processes.</p>
                </div>
              )}

            </div>
          )}

          {/* TAB: Tech Stack & Architecture */}
          {activeTab === "stack_arch" && currentAnalysis?.status === "completed" && (
            <div className="space-y-6">
              
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                
                <div className="glass-panel p-5 rounded-2xl border border-slate-900 flex flex-col">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Languages</h4>
                    <Globe className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="flex-1 space-y-3.5">
                    {currentAnalysis.tech_stack?.languages?.map((lang, idx) => (
                      <div key={idx} className="space-y-1.5">
                        <div className="flex justify-between text-xs font-semibold">
                          <span className="text-slate-250">{lang.name}</span>
                          <span className="text-indigo-400">{lang.confidence}%</span>
                        </div>
                        <div className="w-full h-1 bg-slate-950 rounded-full overflow-hidden">
                          <div 
                            className="bg-indigo-650 h-full rounded-full" 
                            style={{ width: `${lang.confidence}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="glass-panel p-5 rounded-2xl border border-slate-900 flex flex-col">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Frameworks</h4>
                    <Code2 className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="flex-1 space-y-2.5">
                    {currentAnalysis.tech_stack?.frameworks?.map((fw, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-900">
                        <span className="text-xs font-semibold text-slate-200">{fw.name}</span>
                        <span className="text-[9px] font-bold text-indigo-400 uppercase bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/10">
                          {fw.type}
                        </span>
                      </div>
                    ))}
                    {(!currentAnalysis.tech_stack?.frameworks || currentAnalysis.tech_stack.frameworks.length === 0) && (
                      <span className="text-xs text-slate-600 block italic">None detected.</span>
                    )}
                  </div>
                </div>

                <div className="glass-panel p-5 rounded-2xl border border-slate-900 flex flex-col">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Databases</h4>
                    <Database className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="flex-1 space-y-2.5">
                    {currentAnalysis.tech_stack?.databases?.map((db, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-900">
                        <span className="text-xs font-semibold text-slate-200">{db.name}</span>
                        <span className="text-[9px] font-bold text-violet-400 uppercase bg-violet-500/10 px-2 py-0.5 rounded border border-violet-500/10">
                          {db.type}
                        </span>
                      </div>
                    ))}
                    {(!currentAnalysis.tech_stack?.databases || currentAnalysis.tech_stack.databases.length === 0) && (
                      <span className="text-xs text-slate-600 block italic">None detected.</span>
                    )}
                  </div>
                </div>

                <div className="glass-panel p-5 rounded-2xl border border-slate-900 flex flex-col">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Deployment</h4>
                    <Terminal className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="flex-1 space-y-2.5">
                    {currentAnalysis.tech_stack?.deployment?.map((dep, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-900">
                        <span className="text-xs font-semibold text-slate-200">{dep.name}</span>
                        <span className="text-[10px] text-slate-500">confidence: {dep.confidence}%</span>
                      </div>
                    ))}
                    {(!currentAnalysis.tech_stack?.deployment || currentAnalysis.tech_stack.deployment.length === 0) && (
                      <span className="text-xs text-slate-600 block italic">None detected.</span>
                    )}
                  </div>
                </div>

              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                <div className="glass-panel p-6 rounded-2xl border border-slate-900 space-y-5 lg:col-span-2">
                  <div className="flex items-center justify-between border-b border-slate-900 pb-3">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider">Architecture mapping</h3>
                    <span className="bg-indigo-650 text-white font-extrabold text-[9px] px-2.5 py-0.5 rounded-full uppercase tracking-widest border border-indigo-500/20">
                      {currentAnalysis.architecture?.architecture_pattern || "Monolithic"}
                    </span>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">Overview Summary</h4>
                      <p className="text-xs text-slate-350 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-900">
                        {currentAnalysis.architecture?.summary || "No description generated."}
                      </p>
                    </div>

                    <div>
                      <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">Design Patterns Checklist</h4>
                      <div className="flex flex-wrap gap-2">
                        {currentAnalysis.architecture?.design_patterns?.map((dp, idx) => (
                          <span key={idx} className="bg-slate-900 border border-slate-900 text-slate-300 text-xs px-3 py-1 rounded-full font-medium">
                            ✓ {dp}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="glass-panel p-6 rounded-2xl border border-slate-900 space-y-4 flex flex-col">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-slate-900 pb-3">
                    Scalability Suggestions
                  </h3>
                  
                  <ul className="flex-1 space-y-4 overflow-y-auto custom-scrollbar">
                    {currentAnalysis.architecture?.scalability_suggestions?.map((item, idx) => (
                      <li key={idx} className="flex items-start space-x-3 text-xs leading-relaxed text-slate-300">
                        <ArrowRight className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

              </div>

            </div>
          )}

          {/* TAB: Security */}
          {activeTab === "security" && currentAnalysis?.status === "completed" && (
            <div className="space-y-6">
                         <div className="grid grid-cols-2 md:grid-cols-5 gap-4 select-none">
                <div 
                  onClick={() => setSecurityFilter(null)}
                  className={`glass-panel p-4 rounded-xl border cursor-pointer transition-all ${
                    !securityFilter 
                      ? "border-indigo-500 bg-slate-900/80 text-indigo-400 shadow-md shadow-indigo-650/5" 
                      : "border-slate-900/60 text-slate-400 hover:bg-slate-900/30 hover:border-slate-800"
                  }`}
                >
                  <span className="text-[9px] font-bold uppercase tracking-widest block mb-1">Total Issues</span>
                  <span className="text-2xl font-extrabold">{currentAnalysis.security?.summary_stats?.total || 0}</span>
                </div>
                
                <div 
                  onClick={() => setSecurityFilter(securityFilter === "CRITICAL" ? null : "CRITICAL")}
                  className={`glass-panel p-4 rounded-xl border cursor-pointer transition-all ${
                    securityFilter === "CRITICAL"
                      ? "border-red-500 bg-red-950/20 text-red-400 shadow-md shadow-red-650/5"
                      : "border-slate-900/60 bg-red-950/5 text-red-400/70 hover:bg-red-950/10 hover:border-red-950/20"
                  }`}
                >
                  <span className="text-[9px] font-bold uppercase tracking-widest block mb-1">Critical</span>
                  <span className="text-2xl font-extrabold">{currentAnalysis.security?.summary_stats?.critical || 0}</span>
                </div>
                
                <div 
                  onClick={() => setSecurityFilter(securityFilter === "HIGH" ? null : "HIGH")}
                  className={`glass-panel p-4 rounded-xl border cursor-pointer transition-all ${
                    securityFilter === "HIGH"
                      ? "border-orange-500 bg-orange-950/20 text-orange-400 shadow-md shadow-orange-650/5"
                      : "border-slate-900/60 bg-orange-950/5 text-orange-400/70 hover:bg-orange-950/10 hover:border-orange-950/20"
                  }`}
                >
                  <span className="text-[9px] font-bold uppercase tracking-widest block mb-1">High</span>
                  <span className="text-2xl font-extrabold">{currentAnalysis.security?.summary_stats?.high || 0}</span>
                </div>
                
                <div 
                  onClick={() => setSecurityFilter(securityFilter === "MEDIUM" ? null : "MEDIUM")}
                  className={`glass-panel p-4 rounded-xl border cursor-pointer transition-all ${
                    securityFilter === "MEDIUM"
                      ? "border-amber-500 bg-amber-950/20 text-amber-400 shadow-md shadow-amber-650/5"
                      : "border-slate-900/60 bg-amber-950/5 text-amber-400/70 hover:bg-amber-950/10 hover:border-amber-950/20"
                  }`}
                >
                  <span className="text-[9px] font-bold uppercase tracking-widest block mb-1">Medium</span>
                  <span className="text-2xl font-extrabold">{currentAnalysis.security?.summary_stats?.medium || 0}</span>
                </div>
                
                <div 
                  onClick={() => setSecurityFilter(securityFilter === "LOW" ? null : "LOW")}
                  className={`glass-panel p-4 rounded-xl border cursor-pointer transition-all ${
                    securityFilter === "LOW"
                      ? "border-blue-500 bg-blue-950/20 text-blue-400 shadow-md shadow-blue-650/5"
                      : "border-slate-900/60 bg-blue-950/5 text-blue-400/70 hover:bg-blue-950/10 hover:border-blue-950/20"
                  }`}
                >
                  <span className="text-[9px] font-bold uppercase tracking-widest block mb-1">Low</span>
                  <span className="text-2xl font-extrabold">{currentAnalysis.security?.summary_stats?.low || 0}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                <div className="lg:col-span-2 glass-panel p-5 rounded-2xl border border-slate-900 flex flex-col h-[550px]">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3 border-b border-slate-900 pb-3">Static Analysis Vulnerabilities</h3>
                  
                  <div className="flex-1 overflow-y-auto space-y-3.5 custom-scrollbar pr-1">
                    {(() => {
                      const list = currentAnalysis.security?.vulnerabilities || []
                      const filtered = list.filter(v => !securityFilter || v.severity === securityFilter)
                      
                      if (filtered.length === 0) {
                        return (
                          <div className="text-center py-24 text-slate-550 select-none">
                            <Shield className="w-9 h-9 mx-auto text-slate-800 mb-2.5" />
                            <p className="text-xs font-bold text-slate-400">No flaws found</p>
                            <p className="text-[10px] text-slate-600 mt-1 max-w-xs mx-auto leading-relaxed">There are no security issues matching the active filter {securityFilter ? `"${securityFilter}"` : ""}.</p>
                            {securityFilter && (
                              <button
                                type="button"
                                onClick={() => setSecurityFilter(null)}
                                className="mt-4 bg-slate-900 hover:bg-slate-850 text-indigo-400 border border-slate-850 px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-colors"
                              >
                                Clear Filter
                              </button>
                            )}
                          </div>
                        )
                      }
                      
                      return filtered.map((vuln, idx) => (
                        <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-900 space-y-2 text-xs">
                          <div className="flex items-center justify-between">
                            <span className={`px-2 py-0.5 rounded font-extrabold text-[8px] uppercase tracking-wider ${
                              vuln.severity === "CRITICAL" || vuln.severity === "HIGH" 
                                ? "bg-red-500/10 text-red-400 border border-red-500/20" 
                                : vuln.severity === "MEDIUM"
                                ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                            }`}>
                              {vuln.severity}
                            </span>
                            <span className="text-[9px] text-slate-500 font-medium">Tool: {vuln.tool}</span>
                          </div>
                          <h4 className="font-extrabold text-slate-200">{vuln.type}</h4>
                          <p className="text-slate-400 text-[11px] leading-relaxed">{vuln.message}</p>
                          
                          <div className="text-[10px] text-slate-500 font-medium">
                            File: <code className="text-slate-350 font-mono">{vuln.file}:{vuln.line}</code>
                          </div>

                          {vuln.code && (
                            <pre className="p-2.5 rounded-lg bg-slate-950 border border-slate-900 text-red-400/90 font-mono text-[9px] overflow-x-auto custom-scrollbar">
                              {vuln.code}
                            </pre>
                          )}
                        </div>
                      ))
                    })()}
                  </div>
                </div>

                <div className="glass-panel p-6 rounded-2xl border border-slate-900 flex flex-col h-[550px]">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-slate-900 pb-3">Audit Summary report</h3>
                  <div className="flex-1 overflow-y-auto custom-scrollbar mt-3 text-[11px] leading-relaxed text-slate-350 whitespace-pre-wrap">
                    {currentAnalysis.security?.report_markdown || "Security summary report not generated."}
                  </div>
                </div>

              </div>

            </div>
          )}

          {/* TAB: Documentation */}
          {activeTab === "docs" && currentAnalysis?.status === "completed" && (
            <div className="space-y-6">
              
              <div className="flex items-center justify-between border-b border-slate-900 pb-3">
                <div className="glass-panel p-1 rounded-xl border border-slate-900 flex gap-1">
                  {["readme", "architecture", "api_reference", "onboarding"].map((docName) => (
                    <button
                      key={docName}
                      onClick={() => setDocSubTab(docName)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all uppercase ${
                        docSubTab === docName 
                          ? "bg-indigo-600 text-white shadow" 
                          : "text-slate-400 hover:text-white"
                      }`}
                    >
                      {docName.replace("_", " ")}
                    </button>
                  ))}
                </div>

                <button
                  onClick={() => copyToClipboard(currentAnalysis.documentation?.[docSubTab] || "")}
                  className="bg-slate-900 hover:bg-slate-850 text-slate-300 px-3.5 py-1.5 rounded-xl text-xs font-semibold border border-slate-900 flex items-center space-x-1.5 transition-colors"
                >
                  {copiedDoc ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-450" />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy Markdown</span>
                    </>
                  )}
                </button>
              </div>

              <div className="glass-panel p-6 rounded-2xl border border-slate-900 max-w-4xl">
                <MarkdownRenderer content={currentAnalysis.documentation?.[docSubTab] || "No documentation generated for this section."} />
              </div>

            </div>
          )}

          {/* TAB: Interview Prep */}
          {activeTab === "interview" && currentAnalysis?.status === "completed" && (
            <div className="space-y-6">
              
              <div className="glass-panel p-1 rounded-xl border border-slate-900 flex gap-1 max-w-xl">
                {["beginner", "intermediate", "advanced", "system_design"].map((diff) => (
                  <button
                    key={diff}
                    onClick={() => setInterviewSubTab(diff)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all uppercase flex-1 ${
                      interviewSubTab === diff 
                        ? "bg-indigo-600 text-white shadow" 
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    {diff.replace("_", " ")}
                  </button>
                ))}
              </div>

              <div className="space-y-4 max-w-3xl">
                
                {interviewSubTab !== "system_design" && 
                  currentAnalysis.interview_questions?.[interviewSubTab]?.map((q, idx) => {
                    const uniqueIdx = `${interviewSubTab}_${idx}`
                    const isExpanded = expandedQuestions[uniqueIdx]
                    return (
                      <div key={idx} className="glass-panel rounded-2xl border border-slate-900 overflow-hidden transition-all">
                        <div 
                          onClick={() => toggleQuestion(uniqueIdx)}
                          className="p-5 flex items-center justify-between cursor-pointer hover:bg-slate-900/30 transition-colors"
                        >
                          <div className="flex items-center space-x-3 pr-4">
                            <span className="text-[10px] font-bold text-indigo-400 uppercase bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/10">
                              {q.topic || "Core"}
                            </span>
                            <span className="text-xs font-bold text-slate-200">{q.question}</span>
                          </div>
                          {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-500" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
                        </div>
                        
                        {isExpanded && (
                          <div className="p-5 bg-slate-950/40 border-t border-slate-900 text-xs text-slate-300 leading-relaxed">
                            <p className="font-semibold text-slate-400 uppercase tracking-widest text-[9px] mb-2">Suggested Answer:</p>
                            <MarkdownRenderer content={q.answer} />
                          </div>
                        )}
                      </div>
                    )
                  })
                }

                {interviewSubTab === "system_design" && 
                  currentAnalysis.interview_questions?.system_design?.map((sd, idx) => {
                    const uniqueIdx = `system_${idx}`
                    const isExpanded = expandedQuestions[uniqueIdx]
                    return (
                      <div key={idx} className="glass-panel rounded-2xl border border-slate-900 overflow-hidden transition-all">
                        <div 
                          onClick={() => toggleQuestion(uniqueIdx)}
                          className="p-5 flex items-center justify-between cursor-pointer hover:bg-slate-900/30 transition-colors"
                        >
                          <div className="flex items-center space-x-3 pr-4">
                            <span className="text-[10px] font-bold text-violet-400 uppercase bg-violet-500/10 px-2 py-0.5 rounded border border-violet-500/10">
                              System Design
                            </span>
                            <span className="text-xs font-bold text-slate-200">{sd.topic}</span>
                          </div>
                          {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-500" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
                        </div>
                        
                        {isExpanded && (
                          <div className="p-5 bg-slate-950/40 border-t border-slate-900 text-xs text-slate-300 leading-relaxed space-y-4">
                            <div>
                              <p className="font-semibold text-slate-400 uppercase tracking-widest text-[9px] mb-1.5">Discussion Question:</p>
                              <p className="text-slate-200 font-medium">{sd.discussion_question}</p>
                            </div>
                            <div>
                              <p className="font-semibold text-slate-400 uppercase tracking-widest text-[9px] mb-1.5">Evaluation Criteria:</p>
                              <MarkdownRenderer content={sd.evaluation_criteria} />
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })
                }

              </div>

            </div>
          )}

        </div>
      </main>

    </div>
  )
}
