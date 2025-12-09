
import React from 'react';
import InterestCalculator from './components/InterestCalculator';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-base-100 via-base-200 to-base-300 text-gray-100 flex flex-col items-center justify-center p-4 font-sans">
      <div className="w-full max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight">
            Calculadora de Interés
          </h1>
          <p className="text-lg md:text-xl text-gray-300 mt-2">
            Calcula interés simple, compuesto y continuo con facilidad.
          </p>
        </header>
        <main>
          <InterestCalculator />
        </main>
         <footer className="text-center mt-12 text-gray-400 text-sm">
            <p>&copy; {new Date().getFullYear()} Calculadora de Interés Moderna. Todos los derechos reservados.</p>
        </footer>
      </div>
    </div>
  );
};

export default App;
