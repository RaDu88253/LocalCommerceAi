import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import API_URL from './config'; // Importăm URL-ul backend-ului

// --- Flag Components ---
const RomaniaFlag = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 3 2">
    <rect width="1" height="2" fill="#002B7F" />
    <rect width="1" height="2" x="1" fill="#FCD116" />
    <rect width="1" height="2" x="2" fill="#CE1126" />
  </svg>
);
const UKFlag = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 60 30">
    <clipPath id="s"><path d="M0,0 v30 h60 v-30 z"/></clipPath>
    <clipPath id="t"><path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z"/></clipPath>
    <g clipPath="url(#s)">
      <path d="M0,0 v30 h60 v-30 z" fill="#012169"/>
      <path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" strokeWidth="6"/>
      <path d="M0,0 L60,30 M60,0 L0,30" clipPath="url(#t)" stroke="#C8102E" strokeWidth="4"/>
      <path d="M30,0 v30 M0,15 h60" stroke="#fff" strokeWidth="10"/>
      <path d="M30,0 v30 M0,15 h60" stroke="#C8102E" strokeWidth="6"/>
    </g>
  </svg>
);
const GermanyFlag = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 5 3">
    <rect width="5" height="3" fill="#FFCE00"/>
    <rect width="5" height="2" fill="#000"/>
    <rect width="5" height="1" fill="#D00"/>
  </svg>
);
const FranceFlag = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 3 2">
    <rect width="1" height="2" fill="#0055A4"/>
    <rect width="1" height="2" x="1" fill="#fff"/>
    <rect width="1" height="2" x="2" fill="#EF4135"/>
  </svg>
);
const ItalyFlag = () => (
   <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 3 2">
    <rect width="1" height="2" fill="#009246"/>
    <rect width="1" height="2" x="1" fill="#fff"/>
    <rect width="1" height="2" x="2" fill="#CE2B37"/>
  </svg>
);
const SpainFlag = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 750 500">
    <rect width="750" height="500" fill="#c60b1e"/>
    <rect width="750" height="250" y="125" fill="#ffc400"/>
  </svg>
);
const USAFlag = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 1235 650">
    <rect width="1235" height="650" fill="#FFF"/>
    <path d="M0,50H1235M0,150H1235M0,250H1235M0,350H1235M0,450H1235M0,550H1235" stroke="#B22234" strokeWidth="50"/>
    <rect width="494" height="350" fill="#3C3B6E"/>
  </svg>
);
const NetherlandsFlag = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 3 2">
    <rect width="3" height="2" fill="#fff"/>
    <rect width="3" height="1" fill="#AE1C28"/>
    <rect width="3" height="1" y="1" fill="#21468B"/>
  </svg>
);
const AustriaFlag = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 3 2">
    <rect width="3" height="2" fill="#fff"/>
    <rect width="3" height="1" fill="#C8102E"/>
    <rect width="3" height="1" y="1" fill="#C8102E"/>
  </svg>
);

const countryOptions = [
  { code: "+40", name: "RO", flag: <RomaniaFlag /> },
  { code: "+44", name: "UK", flag: <UKFlag /> },
  { code: "+49", name: "DE", flag: <GermanyFlag /> },
  { code: "+33", name: "FR", flag: <FranceFlag /> },
  { code: "+39", name: "IT", flag: <ItalyFlag /> },
  { code: "+34", name: "ES", flag: <SpainFlag /> },
  { code: "+1", name: "US", flag: <USAFlag /> },
  { code: "+31", name: "NL", flag: <NetherlandsFlag /> },
  { code: "+43", name: "AT", flag: <AustriaFlag /> },
];

function RegisterPage() {
  const [formData, setFormData] = useState({
    email: "",
    firstName: "",
    lastName: "",
    password: "",
    confirmPassword: "",
    dob: "",
    phone: "",
    countryCode: "+40",
  });
  const [error, setError] = useState(null);
  const [passwordError, setPasswordError] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const dropdownRef = useRef(null);

  // Handle closing the dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const formatPhoneNumber = (value) => {
    if (!value) return "";
    // 1. Păstrăm doar cifrele
    const phoneNumber = value.replace(/[^\d]/g, "");
    // 2. Limităm la 9 cifre
    const phoneNumberLength = phoneNumber.length;
    if (phoneNumberLength < 4) return phoneNumber;
    if (phoneNumberLength < 7) {
      return `${phoneNumber.slice(0, 3)} ${phoneNumber.slice(3)}`;
    }
    return `${phoneNumber.slice(0, 3)} ${phoneNumber.slice(3, 6)} ${phoneNumber.slice(
      6,
      9
    )}`;
  };

  const handleCountryChange = (code) => {
    setFormData((prevState) => ({
      ...prevState,
      countryCode: code,
    }));
    setIsDropdownOpen(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === "phone") {
      const formattedPhone = formatPhoneNumber(value);
      setFormData((prevState) => ({
        ...prevState,
        phone: formattedPhone,
      }));
    } else {
      setFormData((prevState) => ({ ...prevState, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setPasswordError("");

    // Regex pentru validarea parolei
    const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/;

    if (formData.password !== formData.confirmPassword) {
      setPasswordError("Parolele nu se potrivesc.");
      return;
    }

    if (!passwordRegex.test(formData.password)) {
      setPasswordError("Parola trebuie să aibă minim 8 caractere, o majusculă, o cifră și un caracter special.");
      return;
    }

    setPasswordError(""); // Curăță eroarea dacă totul este în regulă

    // Pregătim datele pentru a fi trimise către backend
    const dataToSend = {
      email: formData.email,
      password: formData.password,
      first_name: formData.firstName,
      last_name: formData.lastName,
      phone_number: `${formData.countryCode}${formData.phone.replace(/\s/g, '')}`, // Combinăm codul țării cu numărul
      date_of_birth: formData.dob,
    };

    try {
      const response = await fetch(`${API_URL}/api/users/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      alert('Înregistrare reușită! Acum te poți autentifica.');
      // Aici ai putea redirecționa utilizatorul către pagina de login
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.message);
    }
  };

  const selectedCountry = countryOptions.find(opt => opt.code === formData.countryCode);

  // Obține data curentă în format YYYY-MM-DD pentru a limita câmpul de dată
  const maxDate = new Date().toISOString().split("T")[0];

  return (
    <div className="min-h-screen flex font-sans">
      {/* Left Side: The "Network" Concept (Identical to Login Page) */}
      <div className="hidden lg:flex w-2/5 flex-col items-center bg-[#EBD9F2] p-12 text-center relative">
        <h1 className="absolute top-24 text-4xl font-bold text-[#752699] leading-tight z-10 max-w-md">
          Going Big with Small Businesses.
        </h1>
        
        {/* Chat Bubbles Concept */}
        <div className="w-full max-w-sm space-y-6 z-10 mt-80">
          {/* User Bubble */}
          <div className="self-end ml-auto max-w-xs">
            <div className="bg-white/60 backdrop-blur-md border border-white/30 rounded-xl rounded-br-none p-4 shadow-xl z-10">
              <p className="text-base text-slate-700">
                Astazi vreau ceva unic!
              </p>
            </div>
          </div>

          {/* AI Bubble */}
          <div className="self-start mr-auto max-w-xs">
            <div className="bg-[#752699]/80 backdrop-blur-md border border-white/20 rounded-xl rounded-bl-none p-4 shadow-xl z-10">
              <p className="text-base text-white">
                Sugestia mea este ...
              </p>
            </div>
          </div>
        </div>
      </div>


      {/* Right Side: The Register Form */}
      <div className="w-full lg:w-3/5 flex items-center justify-center bg-white p-8">
        <div className="w-full max-w-md space-y-4 lg:-mt-16">
          <div>
            <h2 className="text-3xl font-bold text-slate-700 text-center">
              Creează un cont nou
            </h2>
            <p className="mt-2 text-center text-sm text-slate-500">
              Începe călătoria în moda locală.
            </p>
          </div>

          {error && <p className="text-center text-sm text-red-600">{error}</p>}

          <form className="space-y-4" onSubmit={handleSubmit}>
            {/* First and Last Name */}
            <div className="flex flex-col sm:flex-row sm:space-x-4">
              <div className="w-full sm:w-1/2">
                <label htmlFor="firstName" className="block text-sm font-medium text-slate-600">
                  Prenume
                </label>
                <div className="mt-1">
                  <input id="firstName" name="firstName" type="text" required value={formData.firstName} onChange={handleChange} className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-[#752699] focus:border-[#752699]" />
                </div>
              </div>
              <div className="w-full sm:w-1/2 mt-4 sm:mt-0">
                <label htmlFor="lastName" className="block text-sm font-medium text-slate-600">
                  Nume
                </label>
                <div className="mt-1">
                  <input id="lastName" name="lastName" type="text" required value={formData.lastName} onChange={handleChange} className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-[#752699] focus:border-[#752699]" />
                </div>
              </div>
            </div>

            {/* Date of Birth and Phone Number */}
            <div className="flex flex-col sm:flex-row sm:space-x-4">
              <div className="w-full sm:w-1/2">
                <label htmlFor="dob" className="block text-sm font-medium text-slate-600">
                  Data nașterii
                </label>
                <div className="mt-1">
                  <input id="dob" name="dob" type="date" max={maxDate} required value={formData.dob} onChange={handleChange} className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-[#752699] focus:border-[#752699]" />
                </div>
              </div>
              <div className="w-full sm:w-1/2 mt-4 sm:mt-0">
                <label htmlFor="phone" className="block text-sm font-medium text-slate-600">
                  Număr de telefon
                </label>
                {/* Custom Country Code Dropdown */}
                <div className="mt-1 flex rounded-md shadow-sm">
                  <div ref={dropdownRef} className="relative">
                    <button type="button" onClick={() => setIsDropdownOpen(!isDropdownOpen)} className="relative z-10 inline-flex items-center space-x-2 h-full rounded-l-md border border-r-0 border-slate-300 bg-slate-50 px-3 text-slate-600 focus:outline-none focus:ring-1 focus:ring-[#752699] focus:border-[#752699]">
                      {selectedCountry.flag}
                      <span className="text-sm">{selectedCountry.code}</span>
                    </button>
                    {isDropdownOpen && (
                      <div className="absolute top-full -left-1 mt-1 w-40 bg-white rounded-md shadow-lg border border-slate-200 z-20">
                        <ul className="py-1">
                          {countryOptions.map((option) => (
                            <li key={option.code}>
                              <button type="button" onClick={() => handleCountryChange(option.code)} className="w-full flex items-center space-x-3 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100">
                                {option.flag}
                                <span>{option.name} ({option.code})</span>
                              </button>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  <input type="tel" name="phone" id="phone" required value={formData.phone} onChange={handleChange} maxLength="11" className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md border border-slate-300 focus:outline-none focus:ring-1 focus:ring-[#752699] focus:border-[#752699]" />
                </div>
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-600">
                Adresă de email
              </label>
              <div className="mt-1">
                <input id="email" name="email" type="email" required value={formData.email} onChange={handleChange} className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#752699] focus:border-[#752699]" />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-600">
                Parolă
              </label>
              <div className="mt-1">
                <input id="password" name="password" type={showPassword ? "text" : "password"} required value={formData.password} onChange={handleChange} className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#752699] focus:border-[#752699]" />
              </div>
            </div>

            <div>
              <label htmlFor="confirm-password" className="block text-sm font-medium text-slate-600">
                Confirmă parola
              </label>
              <div className="mt-1">
                <input id="confirm-password" name="confirmPassword" type={showPassword ? "text" : "password"} required value={formData.confirmPassword} onChange={handleChange} className="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#752699] focus:border-[#752699]" />
              </div>
              {passwordError && <p className="mt-2 text-sm text-red-600">{passwordError}</p>}
            </div>

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

            <div>
              <button
                type="submit"
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-[#752699] hover:bg-purple-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
              >
                Creează contul
              </button>
            </div>
          </form>

          <p className="text-center text-sm text-slate-500">
            Ai deja cont?{' '}
            <Link to="/login" className="font-medium text-[#752699] hover:text-purple-800">
              Intră în platformă
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;