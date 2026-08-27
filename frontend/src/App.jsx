import { useEffect, useState } from 'react'
import "./style.css";

const API_BASE_URL = "https://ai-life-os-backend-1.onrender.com";

export default function App() {
  const [stats, setStats] = useState(null)
  const [patients, setPatients] = useState([])
  const [healthData, setHealthData] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [aiResponse, setAiResponse] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [editMode, setEditMode] = useState(false)
  const [appointments, setAppointments] = useState([])
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [medicalRecords, setMedicalRecords] = useState([])
  const [activeTab, setActiveTab] = useState('dashboard')
  const [user, setUser] = useState(null)
  const [oldPassword, setOldPassword] = useState('')
  const [newPasswordValue, setNewPasswordValue] = useState('')
  const [newAppointment, setNewAppointment] = useState({
    id: '',
    patient: '',
    doctor: '',
    hospital: '',
    date: '',
    time: '',
    fee: '',
  })
  const [healthScore, setHealthScore] = useState(null)
  const [riskData, setRiskData] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [newMedicalRecord, setNewMedicalRecord] = useState({
    symptoms: '',
    diagnosis: '',
    treatment: '',
    doctor_notes: '',
  })
  const [prescriptions, setPrescriptions] = useState([])
  const [newPrescription, setNewPrescription] = useState({
    medicine: '',
    dosage: '',
    duration: '',
    instructions: '',
  })

  const [newPatient, setNewPatient] = useState({
    name: '',
    age: '',
    gender: '',
    blood_group: '',
    phone: '',
    address: '',
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPatient, setSelectedPatient] = useState(null)
  const [aiTasks, setAiTasks] = useState([])
  const [tasks, setTasks] = useState(() => {
    const savedTasks = localStorage.getItem('tasks')
    return savedTasks
      ? JSON.parse(savedTasks)
      : [
          { id: 1, text: 'Finish AI LIFEOS Frontend', completed: false },
          { id: 2, text: 'Connect Backend API', completed: false },
          { id: 3, text: 'Test Authentication Flow', completed: false },
        ]
  })

  useEffect(() => {
    localStorage.setItem('tasks', JSON.stringify(tasks))
  }, [tasks])

  const [newTask, setNewTask] = useState('')
  const [aiSummary, setAiSummary] = useState('')
  const [aiSummaryLoading, setAiSummaryLoading] = useState(false)
  const [timelineData, setTimelineData] = useState([])
  const [healthSummary, setHealthSummary] = useState(null)
  const [doctorNotes, setDoctorNotes] = useState('')
  const [timelineSummary, setTimelineSummary] = useState('')
  const [notes, setNotes] = useState([])
  const [newNote, setNewNote] = useState({ title: '', content: '' })
  const [showRegister, setShowRegister] = useState(false)
  const [registerName, setRegisterName] = useState('')
  const [editName, setEditName] = useState('')
  const [editEmail, setEditEmail] = useState('')
  const [registerPhone, setRegisterPhone] = useState('')

  // Doctor & Analytics States
  const [doctorSpecialization, setDoctorSpecialization] = useState('')
  const [doctorsList, setDoctorsList] = useState([])
  const [adminAnalytics, setAdminAnalytics] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE_URL}/patients`)
      .then((res) => res.json())
      .then((data) => setPatients(Array.isArray(data) ? data : []))
      .catch((err) => console.error(err))

    fetch(`${API_BASE_URL}/dashboard/stats`)
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.error(err))

    fetch(`${API_BASE_URL}/patients/4/health-score`)
      .then((res) => res.json())
      .then((data) => setHealthData(data))
      .catch((err) => console.error(err))

    fetch(`${API_BASE_URL}/appointments`)
      .then((res) => res.json())
      .then((data) => setAppointments(Array.isArray(data) ? data : []))
      .catch((err) => console.error(err))

    if (token) {
      fetch(`${API_BASE_URL}/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => setUser(data))
        .catch((err) => console.error(err))
    }
  }, [token])

  useEffect(() => {
    if (!selectedPatient) {
      setMedicalRecords([])
      return
    }

    fetch(`${API_BASE_URL}/patients/${selectedPatient.id}/medical-records`)
      .then((res) => res.json())
      .then((data) => {
        setMedicalRecords(Array.isArray(data) ? data : [])
        fetch(`${API_BASE_URL}/patients/${selectedPatient.id}/prescriptions`)
          .then((res) => res.json())
          .then((pData) => setPrescriptions(Array.isArray(pData) ? pData : []))
          .catch(() => setPrescriptions([]))
      })
      .catch(() => setMedicalRecords([]))
  }, [selectedPatient])

  const searchDoctors = async (specOverride) => {
    const specToSearch = specOverride || doctorSpecialization
    if (!specToSearch.trim()) return alert('Please enter or select a specialization')

    try {
      const res = await fetch(`${API_BASE_URL}/doctors/search/${encodeURIComponent(specToSearch.trim())}`)
      const data = await res.json()
      console.log('Search Doctors Response:', data)

      if (Array.isArray(data)) {
        setDoctorsList(data)
      } else if (data.doctors && Array.isArray(data.doctors)) {
        setDoctorsList(data.doctors)
      } else {
        setDoctorsList([])
      }
    } catch (err) {
      console.error('Error searching doctors:', err)
      alert('Error connecting to doctors search API')
    }
  }

  const deleteDoctor = async (doctorId) => {
    if (!window.confirm('Delete doctor?')) return
    try {
      const res = await fetch(`${API_BASE_URL}/doctors/${doctorId}`, { method: 'DELETE' })
      if (res.ok) {
        alert('Doctor deleted ✅')
        setDoctorsList(doctorsList.filter((d) => (d.id || d._id) !== doctorId))
      }
    } catch (err) {
      console.error('Error deleting doctor:', err)
    }
  }

  const updateDoctorFee = async (doctorId, currentName, currentFee) => {
    const newFee = prompt(`Update fee for ${currentName}:`, currentFee)
    if (!newFee) return
    try {
      const res = await fetch(`${API_BASE_URL}/doctors/${doctorId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fee: Number(newFee) }),
      })
      if (res.ok) {
        alert('Doctor updated ✅')
        searchDoctors()
      }
    } catch (err) {
      console.error('Error updating doctor:', err)
    }
  }

  const loadAdminAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/analytics`)
      const data = await res.json()
      setAdminAnalytics(data)
    } catch (err) {
      console.error('Error loading analytics:', err)
    }
  }

  const addPatient = async () => {
    try {
      await fetch(`${API_BASE_URL}/patients`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newPatient, age: Number(newPatient.age) }),
      })
      const res = await fetch(`${API_BASE_URL}/patients`)
      const data = await res.json()
      setPatients(Array.isArray(data) ? data : [])
      setNewPatient({ name: '', age: '', gender: '', blood_group: '', phone: '', address: '' })
      alert('Patient Added Successfully ✅')
    } catch (error) {
      console.error(error)
    }
  }

  const login = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await response.json()
      if (response.ok && data.access_token) {
        localStorage.setItem('token', data.access_token)
        setToken(data.access_token)
        alert('Login Successful ✅')
      } else {
        const errorMsg = typeof data.detail === 'string'
          ? data.detail
          : Array.isArray(data.detail)
            ? data.detail[0]?.msg
            : data.message || 'Login failed ❌'
        alert(errorMsg)
      }
    } catch (error) {
      console.error(error)
      alert('Login Error ❌')
    }
  }

  const register = async () => {
    if (password !== confirmPassword) {
      alert('Passwords do not match ❌')
      return
    }
    try {
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: registerName,
          email,
          password,
          phone: registerPhone || "9999999999"
        }),
      })
      const data = await response.json()
      if (response.ok) {
        setEmail('')
        setPassword('')
        setConfirmPassword('')
        setRegisterPhone('')
        alert(data.message || 'Registered Successfully ✅')
        setShowRegister(false)
        setRegisterName('')
      } else {
        const errorMsg = typeof data.detail === 'string'
          ? data.detail
          : Array.isArray(data.detail)
            ? data.detail[0]?.msg
            : data.message || 'Registration Failed ❌'
        alert(errorMsg)
      }
    } catch (error) {
      console.error(error)
      alert('Registration Failed ❌')
    }
  }

  const askAI = async () => {
    if (!prompt.trim()) return
    if (!selectedPatient) {
      alert('Please select a patient first')
      return
    }
    const currentPrompt = prompt
    setPrompt('')
    setAiLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/ai/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: selectedPatient?.id, prompt: currentPrompt }),
      })
      const data = await response.json()
      const reply = data.response || data.message || 'No response'
      setAiResponse(reply)
      setChatHistory((prev) => [...prev, { prompt: currentPrompt, response: reply }])
      setAiLoading(false)
    } catch (error) {
      console.error('AI Error:', error)
      setAiLoading(false)
    }
  }

  const addTask = () => {
    if (!newTask.trim()) return
    setTasks([...tasks, { id: Date.now(), text: newTask, completed: false }])
    setNewTask('')
  }

  const deleteTask = (id) => {
    setTasks(tasks.filter((task) => task.id !== id))
  }

  const toggleTask = (id) => {
    setTasks(tasks.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t)))
  }

  const generateAITasks = () => {
    let suggestions = ['Drink 2L Water Today', 'Walk 30 Minutes', 'Sleep Before 11 PM']
    setAiTasks(suggestions)
  }

  const deletePatient = async (id) => {
    if (!window.confirm('Are you sure you want to delete this patient?')) return
    try {
      await fetch(`${API_BASE_URL}/patients/${id}`, { method: 'DELETE' })
      setPatients(patients.filter((p) => p.id !== id))
      if (selectedPatient && selectedPatient.id === id) setSelectedPatient(null)
      alert('Patient Deleted ✅')
    } catch (error) {
      console.error(error)
    }
  }

  const updatePatient = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/patients/${selectedPatient.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedPatient),
      })
      const data = await response.json()
      setPatients(patients.map((p) => (p.id === data.id ? data : p)))
      setEditMode(false)
      alert('Patient Updated ✅')
    } catch (error) {
      console.error(error)
    }
  }

  const saveMedicalRecord = async () => {
    if (!selectedPatient) return alert('Please select a patient')
    try {
      await fetch(`${API_BASE_URL}/medical-records`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: selectedPatient.id, ...newMedicalRecord }),
      })
      const res = await fetch(`${API_BASE_URL}/patients/${selectedPatient.id}/medical-records`)
      const updated = await res.json()
      setMedicalRecords(Array.isArray(updated) ? updated : [])
      setNewMedicalRecord({ symptoms: '', diagnosis: '', treatment: '', doctor_notes: '' })
      alert('Medical Record Added Successfully ✅')
    } catch (error) {
      console.error(error)
    }
  }

  const savePrescription = async () => {
    if (!selectedPatient) return alert('Please select a patient')
    try {
      await fetch(`${API_BASE_URL}/prescriptions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: selectedPatient.id, ...newPrescription }),
      })
      const res = await fetch(`${API_BASE_URL}/patients/${selectedPatient.id}/prescriptions`)
      const updated = await res.json()
      setPrescriptions(Array.isArray(updated) ? updated : [])
      setNewPrescription({ medicine: '', dosage: '', duration: '', instructions: '' })
      alert('Prescription Added Successfully ✅')
    } catch (error) {
      console.error(error)
    }
  }

  const addAppointment = async () => {
    try {
      await fetch(`${API_BASE_URL}/appointments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newAppointment, fee: Number(newAppointment.fee) }),
      })
      const res = await fetch(`${API_BASE_URL}/appointments`)
      const updated = await res.json()
      setAppointments(Array.isArray(updated) ? updated : [])
      setNewAppointment({ id: '', patient: '', doctor: '', hospital: '', date: '', time: '', fee: '' })
      alert('Appointment Added Successfully ✅')
    } catch (error) {
      console.error('Error adding appointment:', error)
    }
  }

  const loadTimeline = async () => {
    if (!selectedPatient) return
    try {
      const response = await fetch(`${API_BASE_URL}/patients/${selectedPatient.id}/timeline`)
      const data = await response.json()
      setTimelineData(data.timeline || [])
    } catch (error) {
      console.error(error)
    }
  }

  const loadAiSummary = async () => {
    if (!selectedPatient) return
    try {
      setAiSummaryLoading(true)
      const response = await fetch(`${API_BASE_URL}/patients/${selectedPatient.id}/ai-summary`)
      const data = await response.json()
      setAiSummary(typeof data === 'string' ? data : data.summary || JSON.stringify(data, null, 2))
    } catch (error) {
      console.error(error)
      setAiSummary('Failed to load AI Summary')
    } finally {
      setAiSummaryLoading(false)
    }
  }

  const loadHealthSummary = async () => {
    if (!selectedPatient) return
    try {
      const response = await fetch(`${API_BASE_URL}/patients/${selectedPatient.id}/health-summary`)
      const data = await response.json()
      setHealthSummary(data)
    } catch (error) {
      console.error(error)
    }
  }

  const loadDoctorNotes = async () => {
    if (!selectedPatient) return
    try {
      const response = await fetch(`${API_BASE_URL}/patients/${selectedPatient.id}/doctor-notes`)
      const data = await response.json()
      setDoctorNotes(data.doctor_notes || '')
    } catch (error) {
      console.error(error)
    }
  }

  const loadNotes = async () => {
    if (!selectedPatient) return alert('Select a patient first')
    try {
      const response = await fetch(`${API_BASE_URL}/notes/${selectedPatient.id}`)
      const data = await response.json()
      setNotes(data.notes || [])
    } catch (error) {
      console.error(error)
    }
  }

  const createNote = async () => {
    if (!selectedPatient) return alert('Select a patient first')
    try {
      await fetch(`${API_BASE_URL}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: selectedPatient.id, title: newNote.title, content: newNote.content }),
      })
      setNewNote({ title: '', content: '' })
      loadNotes()
    } catch (error) {
      console.error(error)
    }
  }

  const deleteNote = async (noteId) => {
    try {
      await fetch(`${API_BASE_URL}/notes/${noteId}`, { method: 'DELETE' })
      loadNotes()
    } catch (error) {
      console.error(error)
    }
  }

  const loadTimelineSummary = async () => {
    if (!selectedPatient) return
    try {
      const response = await fetch(`${API_BASE_URL}/patients/${selectedPatient.id}/timeline-summary`)
      const data = await response.json()
      setTimelineSummary(data.summary || '')
    } catch (error) {
      console.error(error)
    }
  }

  const filteredPatients = patients.filter((patient) =>
    (patient.name || '').toLowerCase().includes(searchTerm.toLowerCase())
  )

  const deleteAppointment = async (id) => {
    try {
      await fetch(`${API_BASE_URL}/appointments/${id}`, { method: 'DELETE' })
      setAppointments(appointments.filter((a) => a.id !== id))
      alert('Appointment Deleted ✅')
    } catch (error) {
      console.error(error)
    }
  }

  const changePassword = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/change-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: user?.email, old_password: oldPassword, new_password: newPasswordValue }),
      })
      const data = await response.json()
      alert(data.message)
      setOldPassword('')
      setNewPasswordValue('')
    } catch (error) {
      console.error(error)
    }
  }

  const verifyEmail = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/verify-email?email=${user.email}`, { method: 'POST' })
      const data = await response.json()
      alert(data.message)
      setUser({ ...user, is_verified: 1 })
    } catch (error) {
      console.error(error)
    }
  }

  const updateProfile = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_email: user.email, name: editName || user.name, email: editEmail || user.email }),
      })
      const data = await response.json()
      alert(data.message)
      setUser({ ...user, name: editName || user.name, email: editEmail || user.email })
    } catch (error) {
      console.error(error)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken('')
  }

  if (!token) {
    return (
      <div className="panel" style={{ maxWidth: '400px', margin: '100px auto' }}>
        <h2>{showRegister ? '📝 Register' : '🔐 Login'}</h2>
        {showRegister && (
          <>
            <input
              type="text"
              placeholder="Full Name"
              value={registerName}
              onChange={(e) => setRegisterName(e.target.value)}
            />
            <input
              type="text"
              placeholder="Phone Number"
              value={registerPhone}
              onChange={(e) => setRegisterPhone(e.target.value)}
            />
          </>
        )}
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        {showRegister && (
          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        )}
        {showRegister ? (
          <button onClick={register}>Create Account</button>
        ) : (
          <button onClick={login}>Login</button>
        )}
        <p
          style={{ marginTop: '15px', cursor: 'pointer', color: '#60a5fa' }}
          onClick={() => setShowRegister(!showRegister)}
        >
          {showRegister ? 'Already have an account? Login' : 'New User? Create Account'}
        </p>
      </div>
    )
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div>
          <div className="logo-container">
            <svg className="infinity-logo" viewBox="0 0 100 50" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="infGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#6366F1" />
                  <stop offset="100%" stopColor="#06B6D4" />
                </linearGradient>
              </defs>
              <path
                d="M25,25 C10,10 5,40 25,40 C45,40 55,10 75,10 C95,10 90,40 75,40 C55,40 45,10 25,10 C5,10 10,40 25,25"
                stroke="url(#infGrad)"
                strokeWidth="6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle cx="75" cy="10" r="4" fill="#06B6D4" />
              <circle cx="86" cy="20" r="3" fill="#06B6D4" opacity="0.8" />
              <circle cx="25" cy="40" r="4" fill="#6366F1" />
              <circle cx="14" cy="30" r="3" fill="#6366F1" opacity="0.8" />
            </svg>
            <h2>AI LIFEOS</h2>
          </div>
          <p className="sidebar-subtitle">Personal Operating System</p>
          {user && (
            <>
              <p>👤 {user.email}</p>
              <p>Role: {user.role}</p>
            </>
          )}
        </div>

        <nav>
          <button className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>
            🏠 Dashboard
          </button>
          <button className={activeTab === 'tasks' ? 'active' : ''} onClick={() => setActiveTab('tasks')}>
            ✅ Tasks
          </button>
          <button className={activeTab === 'notes' ? 'active' : ''} onClick={() => setActiveTab('notes')}>
            📝 Notes
          </button>
          <button className={activeTab === 'ai' ? 'active' : ''} onClick={() => setActiveTab('ai')}>
            🤖 AI Assistant
          </button>
          <button className={activeTab === 'settings' ? 'active' : ''} onClick={() => setActiveTab('settings')}>
            ⚙️ Settings
          </button>
          <button onClick={logout}>🚪 Logout</button>
        </nav>
      </aside>

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <>
            <header className="header">
              <h1>AI LIFEOS Dashboard 🚀</h1>
              <p>Manage your productivity with intelligence.</p>
            </header>

            <section className="stats-grid">
              <div className="stat-card">
                <h3>Patients</h3>
                <p>{stats?.total_patients ?? 0}</p>
              </div>
              <div className="stat-card">
                <h3>Medical Records</h3>
                <p>{stats?.total_medical_records ?? 0}</p>
              </div>
              <div className="stat-card">
                <h3>Prescriptions</h3>
                <p>{stats?.total_prescriptions ?? 0}</p>
              </div>
              <div className="stat-card">
                <h3>Appointments</h3>
                <p>{stats?.total_appointments ?? 0}</p>
              </div>
              <div className="stat-card">
                <h3>Health Score</h3>
                <p>{healthData?.health_score ?? 0}</p>
                <small>{healthData?.health_status}</small>
              </div>
            </section>

            <section className="content-grid">
              <div className="panel">
                <h2>Today's Tasks</h2>
                <ul>
                  <li>Review Patient Reports</li>
                  <li>Monitor High Risk Patients</li>
                  <li>Check Pending Appointments</li>
                </ul>
              </div>

              <div className="panel">
                <h2>➕ Add Patient</h2>
                <input
                  type="text"
                  placeholder="Name"
                  value={newPatient.name}
                  onChange={(e) => setNewPatient({ ...newPatient, name: e.target.value })}
                />
                <input
                  type="number"
                  placeholder="Age"
                  value={newPatient.age}
                  onChange={(e) => setNewPatient({ ...newPatient, age: e.target.value })}
                />
                <input
                  type="text"
                  placeholder="Gender"
                  value={newPatient.gender}
                  onChange={(e) => setNewPatient({ ...newPatient, gender: e.target.value })}
                />
                <input
                  type="text"
                  placeholder="Blood Group"
                  value={newPatient.blood_group}
                  onChange={(e) => setNewPatient({ ...newPatient, blood_group: e.target.value })}
                />
                <input
                  type="text"
                  placeholder="Phone"
                  value={newPatient.phone}
                  onChange={(e) => setNewPatient({ ...newPatient, phone: e.target.value })}
                />
                <input
                  type="text"
                  placeholder="Address"
                  value={newPatient.address}
                  onChange={(e) => setNewPatient({ ...newPatient, address: e.target.value })}
                />
                <button onClick={addPatient}>Add Patient</button>
              </div>

              <div className="panel">
                <h2>Recent Patients ({filteredPatients.length})</h2>
                <input
                  type="text"
                  placeholder="🔍 Search Patient"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                {filteredPatients.map((patient) => (
                  <div
                    key={patient.id}
                    onClick={() => {
                      setSelectedPatient(patient)
                      fetch(`${API_BASE_URL}/patients/${patient.id}/health-score`)
                        .then((res) => res.json())
                        .then((data) => setHealthScore(data))
                      fetch(`${API_BASE_URL}/patients/${patient.id}/risk`)
                        .then((res) => res.json())
                        .then((data) => setRiskData(data))
                      fetch(`${API_BASE_URL}/patients/${patient.id}/recommendations`)
                        .then((res) => res.json())
                        .then((data) => setRecommendations(data.recommendations || []))
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    <strong>{patient.name}</strong>
                    <p>Age: {patient.age} | {patient.gender}</p>
                    <p>Blood Group: {patient.blood_group || 'N/A'}</p>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deletePatient(patient.id)
                      }}
                    >
                      Delete
                    </button>
                    <hr />
                  </div>
                ))}
              </div>

              <div className="panel">
                <h2>Appointments ({appointments.length})</h2>
                <input
                  type="text"
                  placeholder="Patient Name"
                  value={newAppointment.patient}
                  onChange={(e) => setNewAppointment({ ...newAppointment, patient: e.target.value })}
                />
                <input
                  type="text"
                  placeholder="Doctor Name"
                  value={newAppointment.doctor}
                  onChange={(e) => setNewAppointment({ ...newAppointment, doctor: e.target.value })}
                />
                <input
                  type="text"
                  placeholder="Hospital"
                  value={newAppointment.hospital}
                  onChange={(e) => setNewAppointment({ ...newAppointment, hospital: e.target.value })}
                />
                <input
                  type="date"
                  value={newAppointment.date}
                  onChange={(e) => setNewAppointment({ ...newAppointment, date: e.target.value })}
                />
                <input
                  type="text"
                  placeholder="Time"
                  value={newAppointment.time}
                  onChange={(e) => setNewAppointment({ ...newAppointment, time: e.target.value })}
                />
                <input
                  type="number"
                  placeholder="Fee"
                  value={newAppointment.fee}
                  onChange={(e) => setNewAppointment({ ...newAppointment, fee: e.target.value })}
                />
                <button onClick={addAppointment}>Add Appointment</button>

                {appointments.map((appointment) => (
                  <div key={appointment.id}>
                    <strong>{appointment.patient}</strong>
                    <p>Doctor: {appointment.doctor}</p>
                    <p>Hospital: {appointment.hospital}</p>
                    <p>Date: {appointment.date}</p>
                    <p>Time: {appointment.time}</p>
                    <p>Fee: ₹{appointment.fee}</p>
                    <button onClick={() => deleteAppointment(appointment.id)}>Delete Appointment</button>
                    <hr />
                  </div>
                ))}
              </div>

              {/* DOCTOR MANAGEMENT PANEL */}
              <div className="panel">
                <h2>👨‍⚕️ Doctor Management</h2>

                <div style={{ display: 'flex', gap: '10px', marginBottom: '15px', flexWrap: 'wrap' }}>
                  <select
                    value={doctorSpecialization}
                    onChange={(e) => {
                      setDoctorSpecialization(e.target.value)
                      if (e.target.value) searchDoctors(e.target.value)
                    }}
                    style={{
                      padding: '10px',
                      borderRadius: '6px',
                      background: '#0f172a',
                      color: 'white',
                      border: '1px solid #374151',
                    }}
                  >
                    <option value="">-- Select Specialization --</option>
                    <option value="Cardiologist">Cardiologist</option>
                    <option value="Dentist">Dentist</option>
                    <option value="General Physician">General Physician</option>
                    <option value="Neurologist">Neurologist</option>
                    <option value="Dermatologist">Dermatologist</option>
                    <option value="Orthopedic">Orthopedic</option>
                  </select>

                  <input
                    type="text"
                    placeholder="Or type specialization..."
                    value={doctorSpecialization}
                    onChange={(e) => setDoctorSpecialization(e.target.value)}
                    style={{ flex: 1, minWidth: '180px' }}
                  />

                  <button onClick={() => searchDoctors()}>Search</button>
                </div>

                {doctorsList.length > 0 ? (
                  doctorsList.map((doc, idx) => (
                    <div
                      key={doc.id || doc._id || idx}
                      style={{
                        border: '1px solid #374151',
                        padding: '12px',
                        marginBottom: '10px',
                        borderRadius: '8px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <div>
                        <strong>{doc.name || doc.doctor_name || 'Doctor'}</strong> ({doc.specialization || doctorSpecialization})
                        <p style={{ margin: '4px 0 0 0', fontSize: '13px', opacity: 0.8 }}>
                          Hospital: {doc.hospital || 'N/A'} | Fee: ₹{doc.fee || 0}
                        </p>
                      </div>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button onClick={() => updateDoctorFee(doc.id || doc._id, doc.name || doc.doctor_name, doc.fee)}>
                          Edit Fee
                        </button>
                        <button
                          onClick={() => deleteDoctor(doc.id || doc._id)}
                          style={{ backgroundColor: '#dc2626' }}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p style={{ opacity: 0.7, marginTop: '10px' }}>
                    No doctors found. Select or type a specialization and click Search.
                  </p>
                )}
              </div>

              {/* ADMIN ANALYTICS PANEL */}
              <div className="panel">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h2>📊 Admin Analytics</h2>
                  <button onClick={loadAdminAnalytics}>Refresh Analytics</button>
                </div>
                {adminAnalytics && (
                  <pre
                    style={{
                      marginTop: '15px',
                      padding: '10px',
                      background: '#0f172a',
                      borderRadius: '8px',
                      overflowX: 'auto',
                    }}
                  >
                    {JSON.stringify(adminAnalytics, null, 2)}
                  </pre>
                )}
              </div>

              <div className="panel">
                <h2>Patient Details</h2>
                {selectedPatient ? (
                  <div>
                    <h3>DEBUG PATIENT: {selectedPatient.name}</h3>
                    <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '15px' }}>
                      <button onClick={() => setEditMode(!editMode)}>{editMode ? 'Cancel' : 'Edit'}</button>
                      <button onClick={loadAiSummary}>
                        {aiSummaryLoading ? 'Loading AI Summary...' : 'Generate AI Summary'}
                      </button>
                      <button onClick={loadTimeline}>Load Timeline</button>
                      <button onClick={loadHealthSummary}>Load Health Summary</button>
                      <button onClick={loadDoctorNotes}>Load Doctor Notes</button>
                      <button onClick={loadTimelineSummary}>Load Timeline Summary</button>
                    </div>

                    {aiSummary && (
                      <div
                        style={{
                          marginTop: '15px',
                          padding: '15px',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                          whiteSpace: 'pre-wrap',
                        }}
                      >
                        <h4>AI Summary</h4>
                        <p>{aiSummary}</p>
                      </div>
                    )}

                    {timelineData.length > 0 && (
                      <div
                        style={{
                          marginTop: '15px',
                          padding: '15px',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                        }}
                      >
                        <h4>Patient Timeline</h4>
                        {timelineData.map((item, index) => (
                          <div
                            key={index}
                            style={{
                              marginBottom: '10px',
                              paddingBottom: '10px',
                              borderBottom: '1px solid #374151',
                            }}
                          >
                            <p>
                              <strong>{item.type}</strong> - {item.title}
                            </p>
                            <small>{item.created_at}</small>
                          </div>
                        ))}
                      </div>
                    )}

                    {timelineSummary && (
                      <div
                        style={{
                          marginTop: '15px',
                          padding: '15px',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                          whiteSpace: 'pre-wrap',
                        }}
                      >
                        <h4>Timeline Summary</h4>
                        <p>{timelineSummary}</p>
                      </div>
                    )}

                    {healthSummary && (
                      <div
                        style={{
                          marginTop: '15px',
                          padding: '15px',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                        }}
                      >
                        <h4>Health Summary</h4>
                        <p><strong>Patient:</strong> {healthSummary.patient?.name}</p>
                        <p><strong>Medical Records:</strong> {healthSummary.medical_records?.length}</p>
                        <p><strong>Prescriptions:</strong> {healthSummary.prescriptions?.length}</p>
                        <p><strong>Lab Reports:</strong> {healthSummary.lab_reports?.length}</p>
                      </div>
                    )}

                    {doctorNotes && (
                      <div
                        style={{
                          marginTop: '15px',
                          padding: '15px',
                          border: '1px solid #374151',
                          borderRadius: '8px',
                          whiteSpace: 'pre-wrap',
                        }}
                      >
                        <h4>Doctor Notes</h4>
                        <p>{doctorNotes}</p>
                      </div>
                    )}

                    <input
                      type="text"
                      value={selectedPatient.name}
                      onChange={(e) => setSelectedPatient({ ...selectedPatient, name: e.target.value })}
                    />
                    <input
                      type="number"
                      value={selectedPatient.age}
                      onChange={(e) => setSelectedPatient({ ...selectedPatient, age: e.target.value })}
                    />
                    <input
                      type="text"
                      value={selectedPatient.gender}
                      onChange={(e) => setSelectedPatient({ ...selectedPatient, gender: e.target.value })}
                    />
                    <input
                      type="text"
                      value={selectedPatient.blood_group || ''}
                      onChange={(e) => setSelectedPatient({ ...selectedPatient, blood_group: e.target.value })}
                    />
                    <input
                      type="text"
                      value={selectedPatient.phone || ''}
                      onChange={(e) => setSelectedPatient({ ...selectedPatient, phone: e.target.value })}
                    />
                    <input
                      type="text"
                      value={selectedPatient.address || ''}
                      onChange={(e) => setSelectedPatient({ ...selectedPatient, address: e.target.value })}
                    />

                    {editMode && <button onClick={updatePatient}>Save Changes</button>}

                    <button
                      onClick={() =>
                        window.open(`${API_BASE_URL}/patients/${selectedPatient.id}/report`, '_blank')
                      }
                    >
                      📄 Download Patient Report
                    </button>

                    <hr />

                    <h3>Health Analytics</h3>
                    {healthScore && (
                      <div>
                        <p><strong>Health Score:</strong> {healthScore.health_score}</p>
                        <p><strong>Status:</strong> {healthScore.health_status}</p>
                      </div>
                    )}

                    {riskData && (
                      <div>
                        <p><strong>Risk Score:</strong> {riskData.risk_score}</p>
                        <p><strong>Risk Level:</strong> {riskData.risk_level}</p>
                        <p><strong>Risk Factors:</strong> {riskData.risk_factors?.join(', ')}</p>
                      </div>
                    )}

                    {recommendations.length > 0 && (
                      <div>
                        <strong>Recommendations:</strong>
                        <ul>
                          {recommendations.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <h3>Add Medical Record</h3>
                    <input
                      type="text"
                      placeholder="Symptoms"
                      value={newMedicalRecord.symptoms}
                      onChange={(e) => setNewMedicalRecord({ ...newMedicalRecord, symptoms: e.target.value })}
                    />
                    <input
                      type="text"
                      placeholder="Diagnosis"
                      value={newMedicalRecord.diagnosis}
                      onChange={(e) => setNewMedicalRecord({ ...newMedicalRecord, diagnosis: e.target.value })}
                    />
                    <input
                      type="text"
                      placeholder="Treatment"
                      value={newMedicalRecord.treatment}
                      onChange={(e) => setNewMedicalRecord({ ...newMedicalRecord, treatment: e.target.value })}
                    />
                    <textarea
                      placeholder="Doctor Notes"
                      value={newMedicalRecord.doctor_notes}
                      onChange={(e) => setNewMedicalRecord({ ...newMedicalRecord, doctor_notes: e.target.value })}
                    />
                    <button onClick={saveMedicalRecord}>Save Medical Record</button>

                    <h3>Medical Records</h3>
                    {medicalRecords.length > 0 ? (
                      medicalRecords.map((record) => (
                        <div
                          key={record.id}
                          style={{
                            border: '1px solid #374151',
                            padding: '10px',
                            marginBottom: '10px',
                            borderRadius: '8px',
                          }}
                        >
                          <p><strong>Symptoms:</strong> {record.symptoms}</p>
                          <p><strong>Diagnosis:</strong> {record.diagnosis}</p>
                          <p><strong>Treatment:</strong> {record.treatment}</p>
                          <p><strong>Doctor Notes:</strong> {record.doctor_notes}</p>
                        </div>
                      ))
                    ) : (
                      <p>No medical records found.</p>
                    )}

                    <h3>Prescriptions</h3>
                    <h4>Add Prescription</h4>
                    <input
                      type="text"
                      placeholder="Medicine"
                      value={newPrescription.medicine}
                      onChange={(e) => setNewPrescription({ ...newPrescription, medicine: e.target.value })}
                    />
                    <input
                      type="text"
                      placeholder="Dosage"
                      value={newPrescription.dosage}
                      onChange={(e) => setNewPrescription({ ...newPrescription, dosage: e.target.value })}
                    />
                    <input
                      type="text"
                      placeholder="Duration"
                      value={newPrescription.duration}
                      onChange={(e) => setNewPrescription({ ...newPrescription, duration: e.target.value })}
                    />
                    <textarea
                      placeholder="Instructions"
                      value={newPrescription.instructions}
                      onChange={(e) => setNewPrescription({ ...newPrescription, instructions: e.target.value })}
                    />
                    <button onClick={savePrescription}>Save Prescription</button>

                    <h4>Prescription History</h4>
                    {prescriptions.length > 0 ? (
                      prescriptions.map((prescription) => (
                        <div
                          key={prescription.id}
                          style={{
                            border: '1px solid #374151',
                            borderRadius: '8px',
                            padding: '12px',
                            marginBottom: '10px',
                          }}
                        >
                          <p><strong>Medicine:</strong> {prescription.medicine}</p>
                          <p><strong>Dosage:</strong> {prescription.dosage}</p>
                          <p><strong>Duration:</strong> {prescription.duration}</p>
                          <p><strong>Instructions:</strong> {prescription.instructions}</p>
                        </div>
                      ))
                    ) : (
                      <p>No prescriptions found.</p>
                    )}
                  </div>
                ) : (
                  <p>Select a patient</p>
                )}
              </div>
            </section>
          </>
        )}

        {activeTab === 'tasks' && (
          <div className="panel" style={{ padding: '24px' }}>
            <h2>✅ Tasks Management</h2>
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', alignItems: 'center' }}>
              <input
                type="text"
                placeholder="Enter new task..."
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                style={{ flex: 1 }}
              />
              <button onClick={addTask}>Add Task</button>
            </div>
            {tasks.map((task) => (
              <div
                key={task.id}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px',
                  marginBottom: '10px',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  gap: '12px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', minWidth: 0, gap: '10px', flex: 1 }}>
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => toggleTask(task.id)}
                    style={{ width: '18px', minWidth: '18px' }}
                  />
                  <span
                    style={{
                      textDecoration: task.completed ? 'line-through' : 'none',
                      opacity: task.completed ? 0.6 : 1,
                      flex: 1,
                      minWidth: 0,
                      whiteSpace: 'normal',
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                    }}
                  >
                    {task.text}
                  </span>
                </div>
                <button onClick={() => deleteTask(task.id)}>Delete</button>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'notes' && (
          <div className="panel" style={{ padding: '24px' }}>
            <h2>📝 Notes Management</h2>
            <div style={{ marginBottom: '20px' }}>
              <button onClick={loadNotes}>Load Notes</button>
            </div>
            <input
              type="text"
              placeholder="Note Title"
              value={newNote.title}
              onChange={(e) => setNewNote({ ...newNote, title: e.target.value })}
              style={{ width: '100%', marginBottom: '10px' }}
            />
            <textarea
              placeholder="Note Content"
              value={newNote.content}
              onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
              rows={4}
              style={{ width: '100%', marginBottom: '10px' }}
            />
            <button onClick={createNote}>Save Note</button>
            <hr style={{ margin: '20px 0' }} />
            {notes.length > 0 ? (
              notes.map((note) => (
                <div
                  key={note.id}
                  style={{
                    border: '1px solid #374151',
                    padding: '12px',
                    borderRadius: '8px',
                    marginBottom: '10px',
                  }}
                >
                  <h3>{note.title}</h3>
                  <p>{note.content}</p>
                  <small>{note.created_at}</small>
                  <br />
                  <button onClick={() => deleteNote(note.id)}>Delete</button>
                </div>
              ))
            ) : (
              <p>No notes found.</p>
            )}
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="panel" style={{ padding: '24px' }}>
            <h2>⚙️ System Settings</h2>
            <div style={{ border: '1px solid #374151', borderRadius: '10px', padding: '20px', marginTop: '20px' }}>
              <h3>👤 User Profile</h3>
              <p><strong>Name:</strong> {user?.name || registerName || 'Not Available'}</p>
              <p><strong>Email:</strong> {user?.email || 'Not Available'}</p>
              <p><strong>Role:</strong> {user?.role || 'User'}</p>
              <input
                type="text"
                placeholder="New Name"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                style={{ width: '100%', marginTop: '10px', marginBottom: '10px' }}
              />
              <input
                type="email"
                placeholder="New Email"
                value={editEmail}
                onChange={(e) => setEditEmail(e.target.value)}
                style={{ width: '100%', marginBottom: '10px' }}
              />
              <button onClick={updateProfile}>Save Profile</button>
            </div>

            <div style={{ border: '1px solid #374151', borderRadius: '10px', padding: '20px', marginTop: '20px' }}>
              <h3>🔒 Security</h3>
              <div style={{ marginTop: '15px' }}>
                <input
                  type="password"
                  placeholder="Old Password"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  style={{ width: '100%', marginBottom: '10px' }}
                />
                <input
                  type="password"
                  placeholder="New Password"
                  value={newPasswordValue}
                  onChange={(e) => setNewPasswordValue(e.target.value)}
                  style={{ width: '100%', marginBottom: '10px' }}
                />
                <button onClick={changePassword}>Change Password</button>
              </div>
            </div>

            <div style={{ border: '1px solid #374151', borderRadius: '10px', padding: '20px', marginTop: '20px' }}>
              <h3>📧 Email Verification</h3>
              <p>Status: {user?.is_verified ? 'Verified ✅' : 'Not Verified ❌'}</p>
              <button onClick={verifyEmail}>Verify Email</button>
            </div>

            <div style={{ marginTop: '20px' }}>
              <button onClick={logout}>🚪 Logout</button>
            </div>
          </div>
        )}

        {activeTab === 'ai' && (
          <div className="panel ai-workspace">
            <div className="ai-header">
              <div>
                <h2>🤖 AI LIFEOS Assistant</h2>
                <p>Intelligent health & lifestyle assistant</p>
              </div>
              <span className="ai-status">● Online</span>
            </div>
            <div style={{ marginTop: '15px', marginBottom: '15px' }}>
              <button onClick={generateAITasks}>🧠 Generate AI Tasks</button>
            </div>

            {selectedPatient && (
              <div
                style={{
                  marginTop: '15px',
                  marginBottom: '15px',
                  padding: '15px',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  background: '#111827',
                }}
              >
                <h3>📊 Patient Snapshot</h3>
                <p><strong>Patient:</strong> {selectedPatient.name}</p>
                {healthScore && (
                  <>
                    <p><strong>Health Score:</strong> {healthScore.health_score}</p>
                    <p><strong>Status:</strong> {healthScore.health_status}</p>
                  </>
                )}
                {riskData && (
                  <>
                    <p><strong>Risk Score:</strong> {riskData.risk_score}</p>
                    <p><strong>Risk Level:</strong> {riskData.risk_level}</p>
                  </>
                )}
              </div>
            )}

            {aiTasks.length > 0 && (
              <div
                style={{
                  marginBottom: '15px',
                  padding: '15px',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  background: '#0f172a',
                }}
              >
                <h3>🧠 AI Suggested Tasks</h3>
                {aiTasks.map((task, index) => (
                  <div key={index} style={{ marginBottom: '10px' }}>{task}</div>
                ))}
              </div>
            )}

            <div className="ai-chat-box">
              {chatHistory.length === 0 ? (
                <div className="ai-welcome">
                  <div className="ai-icon">🤖</div>
                  <h3>How can I help you?</h3>
                  <p>Ask me about patient health, lifestyle, sleep, exercise, or general health guidance.</p>
                </div>
              ) : (
                chatHistory.map((chat, index) => (
                  <div className="chat-message" key={index}>
                    <div className="user-message">
                      <strong>👤 You</strong>
                      <p>{chat.prompt}</p>
                    </div>
                    <div className="ai-message">
                      <strong>🤖 AI LIFEOS</strong>
                      <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>
                        {chat.response}
                      </pre>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label><strong>Select Patient:</strong></label>
              <select
                onChange={(e) => {
                  const patient = patients.find((p) => p.id === Number(e.target.value))
                  setSelectedPatient(patient || null)
                  setPrompt('')
                  if (patient) {
                    fetch(`${API_BASE_URL}/patients/${patient.id}/health-score`)
                      .then((res) => res.json())
                      .then((data) => setHealthScore(data))
                    fetch(`${API_BASE_URL}/patients/${patient.id}/risk`)
                      .then((res) => res.json())
                      .then((data) => setRiskData(data))
                    fetch(`${API_BASE_URL}/patients/${patient.id}/recommendations`)
                      .then((res) => res.json())
                      .then((data) => setRecommendations(data.recommendations || []))
                    fetch(`${API_BASE_URL}/ai/history/${patient.id}`)
                      .then((res) => res.json())
                      .then((data) => {
                        const chats = []
                        let currentChat = null
                        ;(data.history || []).forEach((item) => {
                          if (item.role === 'user') {
                            currentChat = { prompt: item.message, response: '' }
                            chats.push(currentChat)
                          } else if (item.role === 'assistant' && currentChat) {
                            currentChat.response = item.message
                          }
                        })
                        setChatHistory(chats)
                      })
                      .catch((err) => console.error(err))
                  } else {
                    setChatHistory([])
                  }
                }}
                style={{
                  width: '100%',
                  padding: '10px',
                  marginTop: '8px',
                  borderRadius: '8px',
                  background: '#0f172a',
                  color: 'white',
                  border: '1px solid #374151',
                }}
              >
                <option value="">Select a patient</option>
                {patients.map((patient) => (
                  <option key={patient.id} value={patient.id}>
                    {patient.name} — Age {patient.age}
                  </option>
                ))}
              </select>
            </div>

            <div className="ai-input-area">
              <textarea
                placeholder="Ask AI about patient health..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows="3"
              />
              <button onClick={askAI} disabled={aiLoading}>
                {aiLoading ? 'Thinking... 🤖' : 'Send 🚀'}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}