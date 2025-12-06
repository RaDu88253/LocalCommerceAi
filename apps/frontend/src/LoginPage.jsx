import React, { useState } from "react";
import { Link } from "react-router-dom";
import API_URL from './config'; // Importăm URL-ul backend-ului

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Backend-ul se așteaptă la date de tip 'form-data' pentru acest endpoint,
    // nu JSON, deoarece folosește OAuth2PasswordRequestForm.
    const formData = new URLSearchParams();
    formData.append('username', email); // Standardul OAuth2 folosește 'username', chiar dacă noi trimitem un email
    formData.append('password', password);

    try {
      const response = await fetch(`${API_URL}/api/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Authentication failed');
      }

      const data = await response.json();
      console.log('Login successful!', data);

      // Salvăm token-ul în localStorage pentru a-l folosi ulterior
      localStorage.setItem('accessToken', data.access_token);
      
      alert('Login reușit! Token-ul a fost salvat.');
      // Aici ai putea redirecționa utilizatorul, de ex. cu useNavigate()

    } catch (err) {
      console.error('Login error:', err);
      // Asigurăm că afișăm un mesaj text, chiar dacă eroarea este un obiect.
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('A apărut o eroare neașteptată. Vă rugăm să încercați din nou.');
      }
    }
  };

  return (
    <div className="min-h-screen flex font-sans">
      {/* Left Side: The "Network" Concept */}
      <div className="hidden lg:flex w-2/5 flex-col items-center justify-center bg-[#EBD9F2] p-12 text-center relative">
        {/* Container for text, using flex to push items to top and bottom */}
        <div className="w-full max-w-md z-20 flex flex-col justify-between h-[40rem]">
          <h1 className="text-4xl font-bold text-[#752699] leading-tight">
            Going Big with Small Businesses.
          </h1>
          <p className="text-lg text-[#4A4453]">
            Conectăm cererea ta complexă cu oferta locală fragmentată.
          </p>
        </div>

        {/* Hub and Spoke Diagram */}
        <div className="absolute w-96 h-96">
          {/* Central Node */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-24 h-24 rounded-full bg-[#752699] flex items-center justify-center text-white font-bold text-2xl z-10">
            AI
          </div>

          {/* Satellite Nodes & Lines */}
          {[
            { name: "Ateliere" },
            { name: "Designeri" },
            { name: "Boutique" },
            { name: "Artizani" },
            { name: "Unicitate" },
          ].map((node, index, arr) => {
            const angle = (index / arr.length) * 2 * Math.PI - Math.PI / 2; // Start from top
            const radius = 144; // 9rem
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;

            return (
              <React.Fragment key={node.name}>
                {/* Line */}
                <div className="absolute top-1/2 left-1/2 w-[9rem] h-px bg-[#752699] origin-left" style={{ transform: `rotate(${angle * (180 / Math.PI)}deg)` }} />
                {/* Node */}
                <div className="absolute top-1/2 left-1/2 w-20 h-20 rounded-full bg-white shadow-lg flex items-center justify-center z-10 text-center" style={{ transform: `translate(-50%, -50%) translate(${x}px, ${y}px)` }}>
                  <span className="text-xs font-semibold text-[#475569]">{node.name}</span>
                </div>
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Right Side: The Login Form */}
      <div className="w-full lg:w-3/5 flex items-center justify-center bg-white p-8">
        <div className="w-full max-w-md space-y-8 lg:-mt-16">
          <div>
            <h2 className="text-3xl font-bold text-slate-700 text-center">
              Logare în cont
            </h2>
            <p className="mt-2 text-center text-sm text-slate-500">
              Acces la moda locală inteligentă.
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-600">
                Adresă de email
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#752699] focus:border-[#752699]"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-slate-600"
              >
                Parolă
              </label>
              <div className="mt-1">
                <input
                  aria-label="Parolă"
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#752699] focus:border-[#752699]"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="show-password"
                  name="show-password"
                  type="checkbox"
                  checked={showPassword}
                  onChange={() => setShowPassword(!showPassword)}
                  className="h-4 w-4 rounded border-slate-300 text-[#752699] focus:ring-[#752699]"
                />
                <label htmlFor="show-password" className="ml-2 block text-sm text-slate-600">
                  Afișează parola
                </label>
              </div>

              <div className="text-sm">
                <a href="#" className="font-medium text-[#752699] hover:text-purple-800">
                  Ai uitat parola?
                </a>
              </div>
            </div>

            {error && <p className="text-center text-sm text-red-600">{error}</p>}

            <div>
              <button
                type="submit"
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-[#752699] hover:bg-purple-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
              >
                Intră în platformă
              </button>
            </div>
          </form>

          <p className="text-center text-sm text-slate-500">
            Nu ai cont?{' '}
            <Link to="/register" className="font-medium text-[#752699] hover:text-purple-800">
              Creează un cont nou
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;