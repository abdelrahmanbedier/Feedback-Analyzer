import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';
import SentimentPieChart from './SentimentPieChart';

const productOptions = [
  "Acura", "Audi", "BMW", "Cadillac", "Chevrolet",
  "Ferrari", "Ford", "GMC", "Honda", "Hyundai",
  "Jaguar", "Jeep", "Kia", "Lamborghini", "Land Rover",
  "Lexus", "Mazda", "Mercedes-Benz", "Nissan",
  "Porsche", "Subaru", "Tesla", "Toyota", "Volkswagen", "Volvo"
];
const sentimentOptions = ["All", "positive", "negative", "neutral"];
const languageOptions = [
  { name: "All Languages", code: "All" },
  { name: "English", code: "en" },
  { name: "French", code: "fr" },
  { name: "Spanish", code: "es" },
  { name: "German", code: "de" },
  { name: "Japanese", code: "ja" },
  { name: "Chinese (Mandarin)", code: "zh" },
  { name: "Russian", code: "ru" },
  { name: "Arabic", code: "ar" },
  { name: "Portuguese", code: "pt" },
  { name: "Italian", code: "it" },
  { name: "To Be Reviewed", code: "review" },
  { name: "Other Languages", code: "Others" }
];

const PAGE_SIZE = 5;

function App() {
  const [feedbackText, setFeedbackText] = useState('');
  const [product, setProduct] = useState(productOptions[0]);
  const [submittedMessage, setSubmittedMessage] = useState('');
  const [feedbackList, setFeedbackList] = useState([]);
  const [stats, setStats] = useState(null);
  const [isAdminMode, setIsAdminMode] = useState(false);
  const [filterProduct, setFilterProduct] = useState("All");
  const [filterSentiment, setFilterSentiment] = useState("All");
  const [filterLanguage, setFilterLanguage] = useState("All");
  const [isLoading, setIsLoading] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');
  const [editSentiment, setEditSentiment] = useState('neutral');
  const [messageType, setMessageType] = useState('success');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [passwordInput, setPasswordInput] = useState('');

  const fetchStats = useCallback(() => {
    axios.get('http://localhost:8000/api/stats')
      .then(response => setStats(response.data))
      .catch(error => console.error("Error fetching stats!", error));
  }, []);

  const fetchFeedback = useCallback(() => {
    const params = new URLSearchParams();
    if (filterProduct !== "All") params.append('product', filterProduct);
    if (filterSentiment !== "All") params.append('sentiment', filterSentiment);
    if (filterLanguage !== "All") params.append('original_language', filterLanguage);
    if (isAdminMode) params.append('show_all', 'true');
    params.append('page', currentPage);
    params.append('page_size', PAGE_SIZE);

    axios.get(`http://localhost:8000/api/feedback`, { params })
      .then(response => {
        setFeedbackList(response.data.items);
        setTotalPages(Math.ceil(response.data.total_count / PAGE_SIZE));
      })
      .catch(error => console.error("Error fetching feedback list!", error));
  }, [filterProduct, filterSentiment, filterLanguage, isAdminMode, currentPage]);

  useEffect(() => {
    fetchStats();
    const savedAdminStatus = localStorage.getItem('isAdmin');
    if (savedAdminStatus === 'true') {
      setIsAdminMode(true);
    }
  }, [fetchStats]);

  useEffect(() => {
    fetchFeedback();
  }, [fetchFeedback]);

  const handleAdminLogin = () => {
  setShowLoginModal(true);
  };

  const handlePasswordSubmit = (event) => {
  event.preventDefault(); // Prevent form from reloading the page
  if (passwordInput === 'admin123') {
    setIsAdminMode(true);
    localStorage.setItem('isAdmin', 'true');
    setShowLoginModal(false); // Close the modal on success
    setPasswordInput(''); // Clear the password input
  } else {
    alert('Incorrect password.');
    setPasswordInput(''); // Clear the password input
  }
};

  const handleAdminLogout = () => {
    setIsAdminMode(false);
    localStorage.removeItem('isAdmin');
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setIsLoading(true);
    const feedbackData = { original_text: feedbackText, product: product };
    axios.post('http://localhost:8000/api/feedback', feedbackData)
      .then(response => {
        setFeedbackText('');
        setProduct(productOptions[0]);
        if (response.data.status === 'review') {
          setSubmittedMessage('Thank you! Your feedback is being reviewed by an admin.');
          setMessageType('review');
        } else {
          setSubmittedMessage('Thank you for your feedback!');
          setMessageType('success');
        }
        fetchFeedback();
        fetchStats();
        setTimeout(() => setSubmittedMessage(''), 5000);
        setIsLoading(false);
      })
      .catch(error => {
        setSubmittedMessage('Sorry, something went wrong. Please try again.');
        setMessageType('error');
        console.error("Error submitting form!", error);
        setIsLoading(false);
      });
  };

  const handleDelete = (feedbackId) => {
    if (window.confirm('Are you sure you want to delete this feedback?')) {
      axios.delete(`http://localhost:8000/api/feedback/${feedbackId}`)
        .then(() => {
          fetchFeedback();
          fetchStats();
        })
        .catch(error => {
          console.error("There was an error deleting the feedback!", error);
          alert("Could not delete feedback.");
        });
    }
  };

  const handleEdit = (item) => {
    setEditingId(item.id);
    setEditText(item.original_text);
    setEditSentiment('neutral');
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditText('');
    setEditSentiment('neutral');
  };

  const handleUpdate = (feedbackId) => {
    const updatedData = {
      translated_text: editText,
      sentiment: editSentiment,
    };
    axios.put(`http://localhost:8000/api/feedback/${feedbackId}`, updatedData)
      .then(() => {
        handleCancelEdit();
        fetchFeedback();
        fetchStats();
      })
      .catch(error => console.error("Error updating feedback!", error));
  };

  const handleFilterProductChange = (e) => {
    setFilterProduct(e.target.value);
    setCurrentPage(1);
  };
  const handleFilterSentimentChange = (e) => {
    setFilterSentiment(e.target.value);
    setCurrentPage(1);
  };
  const handleFilterLanguageChange = (e) => {
    setFilterLanguage(e.target.value);
    setCurrentPage(1);
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };
  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  return (
    <div className="App">
      <header className={`App-header ${isAdminMode ? 'admin' : ''}`}>
        <h1>Customer Cars Feedback</h1>
        {!isAdminMode ? (
          <button onClick={handleAdminLogin} className="admin-button">Admin Login</button>
        ) : (
          <button onClick={handleAdminLogout} className="admin-button logout-button">Logout</button>
        )}
      </header>
      
      {!isAdminMode && (
        <div className={`submission-section ${isAdminMode ? 'admin' : ''}`}>
          <form onSubmit={handleSubmit}>
            <select value={product} onChange={(e) => setProduct(e.target.value)} className="product-input">
              {productOptions.map(option => <option key={option} value={option}>{option}</option>)}
            </select>
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="Enter your feedback in any language..."
              rows="5"
              cols="60"
              required
            />
            <br />
            <button type="submit" className={isAdminMode ? 'admin' : ''} disabled={isLoading}>
              {isLoading ? 'Analyzing...' : 'Submit Feedback'}
            </button>
          </form>
          {submittedMessage && <p className={`submission-message ${messageType}`}>{submittedMessage}</p>}
        </div>
      )}

      <main className="main-content-layout">
        <div className="feedback-column">
          <h2>Submitted Feedback</h2>
          <div className="feedback-list">
            {feedbackList.map(item => (
              <div key={item.id} className="feedback-item">
                {editingId === item.id ? (
                  <div className="edit-form">
                    <p><strong>Product:</strong> {item.product}</p>
                    <p><strong>Original:</strong> {item.original_text}</p>
                    <label>Manual Translation:</label>
                    <textarea value={editText} onChange={(e) => setEditText(e.target.value)} rows="3" />
                    <label>Manual Sentiment:</label>
                    <select value={editSentiment} onChange={(e) => setEditSentiment(e.target.value)}>
                      <option value="positive">positive</option>
                      <option value="neutral">neutral</option>
                      <option value="negative">negative</option>
                    </select>
                    <div className="edit-buttons">
                      <button onClick={() => handleUpdate(item.id)} className="save-button">Approve & Post</button>
                      <button onClick={handleCancelEdit} className="cancel-button">Cancel</button>
                    </div>
                  </div>
                ) : (
                  <div>
                    {item.product && <p><strong>Product:</strong> {item.product}</p>}
                    <p><strong>Original:</strong> {item.original_text}</p>
                    <p><strong>Translation:</strong> {item.translated_text}</p>
                    <p><strong>Sentiment:</strong> <span className={`sentiment-${item.sentiment}`}>{item.sentiment}</span></p>
                    
                    {(item.status === 'review' || (item.was_reviewed && item.status === 'published')) && isAdminMode && (
                      <button onClick={() => handleEdit(item)} className="edit-button">
                        {item.status === 'review' ? 'Review & Post' : 'Edit'}
                      </button>
                    )}
                    {isAdminMode && (
                       <button onClick={() => handleDelete(item.id)} className="delete-button">
                         Delete
                       </button>
                     )}
                  </div>
                )}
              </div>
            ))}
          </div>
          {totalPages > 1 && (
            <div className="pagination-controls">
              <button onClick={handlePrevPage} disabled={currentPage === 1}>
                &laquo; Previous
              </button>
              <span>Page {currentPage} of {totalPages}</span>
              <button onClick={handleNextPage} disabled={currentPage === totalPages}>
                Next &raquo;
              </button>
            </div>
          )}
        </div>

        <div className="dashboard-column">
          <div className="dashboard">
            <div className="dashboard-header">
              <h2>Dashboard</h2>
            </div>
            {stats ? (
              <div className="dashboard-content">
                <div className="stats-container">
                  <div className="stat-card"><h3>{stats.positive_count}</h3><p>Positive ({stats.positive_percentage.toFixed(1)}%)</p></div>
                  <div className="stat-card"><h3>{stats.neutral_count}</h3><p>Neutral ({stats.neutral_percentage.toFixed(1)}%)</p></div>
                  <div className="stat-card"><h3>{stats.negative_count}</h3><p>Negative ({stats.negative_percentage.toFixed(1)}%)</p></div>
                  <div className="stat-card"><h3>{stats.total_count}</h3><p>Total Submissions</p></div>
                </div>
                <div className="chart-container">
                  <SentimentPieChart stats={stats} />
                </div>
              </div>
            ) : <p>Loading stats...</p>}

            {isAdminMode && (
              <div className="admin-controls">
                <h3>Admin Controls</h3>
                <div className="filters">
                  <select value={filterProduct} onChange={handleFilterProductChange}>
                    <option value="All">All Products</option>
                    {productOptions.map(p => <option key={p} value={p}>{p}</option>)}
                  </select>
                  <select value={filterSentiment} onChange={handleFilterSentimentChange}>
                    {sentimentOptions.map(s => <option key={s} value={s}>{s === 'All' ? 'All Sentiments' : s}</option>)}
                  </select>
                  <select value={filterLanguage} onChange={handleFilterLanguageChange}>
                      {languageOptions.map(lang => <option key={lang.code} value={lang.code}>{lang.name}</option>)}
                  </select>
                </div>
              </div>
            )}
          </div>
        </div>
        
      </main>
       {/* --- NEW: Login Modal --- */}
        {showLoginModal && (
          <div className="modal-overlay">
            <div className="modal-content">
              <h2>Admin Login</h2>
              <form onSubmit={handlePasswordSubmit}>
                <input
                  type="password"
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  placeholder="Enter password..."
                  autoFocus
                />
                <div className="modal-buttons">
                  <button type="submit">Login</button>
                  <button type="button" onClick={() => setShowLoginModal(false)}>Cancel</button>
                </div>
              </form>
            </div>
          </div>
        )} 
    </div>
    
  ); 
}

export default App;