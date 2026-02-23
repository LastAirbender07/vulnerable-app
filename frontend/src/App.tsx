import { useState, useEffect } from 'react';
import './App.css';

// VULNERABILITY 1: API keys hardcoded in frontend
const API_KEY = "sk_live_51HxyzABCDEF123456789";
const FIREBASE_CONFIG = {
    apiKey: "AIzaSyDOCAbC123dEf456GhI789jKl012-MnO",
    authDomain: "myapp.firebaseapp.com",
    projectId: "myapp-12345"
};

// VULNERABILITY 2: Sensitive credentials in code
const ADMIN_PASSWORD = "admin123";
const API_URL = 'http://localhost:5000/api';

function App() {
    const [posts, setPosts] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [token, setToken] = useState('');
    const [newPost, setNewPost] = useState({ title: '', content: '' });
    const [pingHost, setPingHost] = useState('');

    // VULNERABILITY 3: Token stored in localStorage (XSS can steal it)
    useEffect(() => {
        const savedToken = localStorage.getItem('auth_token');
        if (savedToken) {
            setToken(savedToken);
        }
    }, []);

    // VULNERABILITY 4: No input sanitization before API calls
    const handleLogin = async () => {
        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();

            if (data.token) {
                // VULNERABILITY 5: Storing sensitive data in localStorage
                localStorage.setItem('auth_token', data.token);
                localStorage.setItem('username', data.username);
                localStorage.setItem('is_admin', data.is_admin);
                setToken(data.token);
                alert('Login successful!');
            } else {
                alert('Login failed');
            }
        } catch (err) {
            // VULNERABILITY 6: Detailed error messages exposed to user
            alert('Error: ' + err.message);
        }
    };

    // VULNERABILITY 7: Missing CSRF token in state-changing requests
    const fetchPosts = async () => {
        try {
            const response = await fetch(`${API_URL}/posts`);
            const data = await response.json();
            setPosts(data);
        } catch (err) {
            console.error(err);
        }
    };

    // VULNERABILITY 8: SQL injection via search (no sanitization)
    const handleSearch = async () => {
        try {
            // Directly passing user input to backend
            const response = await fetch(`${API_URL}/posts/search?q=${searchTerm}`);
            const data = await response.json();
            setPosts(data);
        } catch (err) {
            console.error(err);
        }
    };

    // VULNERABILITY 9: No CSRF protection
    const createPost = async () => {
        try {
            await fetch(`${API_URL}/posts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...newPost,
                    author_id: 1
                })
            });
            setNewPost({ title: '', content: '' });
            fetchPosts();
        } catch (err) {
            console.error(err);
        }
    };

    // VULNERABILITY 10: Command injection via user input
    const handlePing = async () => {
        try {
            const response = await fetch(`${API_URL}/ping`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ host: pingHost })
            });
            const data = await response.json();
            alert(data.output);
        } catch (err) {
            alert('Ping failed: ' + err.message);
        }
    };

    // VULNERABILITY 11: Sensitive data logged to console
    console.log('API_KEY:', API_KEY);
    console.log('Firebase Config:', FIREBASE_CONFIG);
    console.log('Auth Token:', token);

    useEffect(() => {
        fetchPosts();
    }, []);

    return (
        <div className="App">
            <header>
                <h1>Vulnerable Blog App</h1>
                <p>For Security Testing Purposes Only</p>
            </header>

            {!token ? (
                <div className="login-section">
                    <h2>Login</h2>
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <button onClick={handleLogin}>Login</button>
                    <p style={{ color: '#888', fontSize: '12px' }}>
                        Default credentials: admin/admin
                    </p>
                </div>
            ) : (
                <>
                    <div className="search-section">
                        <h2>Search Posts</h2>
                        <input
                            type="text"
                            placeholder="Search..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                        <button onClick={handleSearch}>Search</button>
                    </div>

                    <div className="create-section">
                        <h2>Create Post</h2>
                        <input
                            type="text"
                            placeholder="Title"
                            value={newPost.title}
                            onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                        />
                        <textarea
                            placeholder="Content (HTML allowed)"
                            value={newPost.content}
                            onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                        />
                        <button onClick={createPost}>Create Post</button>
                    </div>

                    <div className="ping-section">
                        <h2>Network Tool</h2>
                        <input
                            type="text"
                            placeholder="Host to ping"
                            value={pingHost}
                            onChange={(e) => setPingHost(e.target.value)}
                        />
                        <button onClick={handlePing}>Ping</button>
                    </div>
                </>
            )}

            <div className="posts-section">
                <h2>Posts</h2>
                {posts.map((post) => (
                    <div key={post.id} className="post-card">
                        <h3>{post.title}</h3>
                        {/* VULNERABILITY 12: XSS via dangerouslySetInnerHTML */}
                        <div dangerouslySetInnerHTML={{ __html: post.content }} />
                        <p className="post-meta">
                            Posted at: {post.created_at}
                        </p>
                    </div>
                ))}
            </div>

            {/* VULNERABILITY 13: Inline script tags (CSP bypass potential) */}
            <script dangerouslySetInnerHTML={{
                __html: `
                    console.log('Inline script executing...');
                    window.apiKey = '${API_KEY}';
                `
            }} />
        </div>
    );
}

export default App;
