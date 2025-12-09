import React, { useState, useMemo } from 'react';
import type { InterestType, TimeUnit, Result } from '../types';
import ResultCard from './ResultCard';
import { InfoIcon } from './icons/InfoIcon';
import { SyncIcon } from './icons/SyncIcon';
import { SpinnerIcon } from './icons/SpinnerIcon';

const InterestCalculator: React.FC = () => {
  const [principal, setPrincipal] = useState<string>('1000');
  const [rate, setRate] = useState<string>('5');
  const [inflation, setInflation] = useState<string>('3');
  const [time, setTime] = useState<string>('10');
  const [timeUnit, setTimeUnit] = useState<TimeUnit>('years');
  const [compoundingFrequency, setCompoundingFrequency] = useState<number>(12);
  const [interestType, setInterestType] = useState<InterestType>('compound');
  const [result, setResult] = useState<Result | null>(null);
  const [isLoadingInflation, setIsLoadingInflation] = useState(false);

  const compoundingOptions = [
    { label: 'Anual', value: 1 },
    { label: 'Semestral', value: 2 },
    { label: 'Trimestral', value: 4 },
    { label: 'Mensual', value: 12 },
    { label: 'Diario', value: 365 },
  ];

  const fetchInflationRate = async () => {
    setIsLoadingInflation(true);
    const url = 'https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176802&menu=ultiDatos&idp=1254735976607';

    try {
      const proxyUrl = `https://cors.sh/${url}`;
      const response = await fetch(proxyUrl);
      if (!response.ok) {
        throw new Error(`Error al contactar el servicio proxy: ${response.statusText}`);
      }
      const data = await response.json();
      const html = data.contents;

      const match = html.match(/variación anual en el (.*?)%/);
      if (match && match[1]) {
        const inflationValue = parseFloat(match[1].replace(',', '.'));
        if (!isNaN(inflationValue)) {
          setInflation(inflationValue.toString());
        } else {
          throw new Error('No se pudo convertir el valor de inflación a un número.');
        }
      } else {
        throw new Error('No se pudo encontrar el valor de la inflación en la página.');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Error al obtener la inflación:', errorMessage);
      alert(`No se pudo obtener el dato de inflación.\n\nDetalle: ${errorMessage}`);
    } finally {
      setIsLoadingInflation(false);
    }
  };


  const handleCalculate = () => {
    const p = parseFloat(principal);
    const rPercent = parseFloat(rate);
    const inflationPercent = parseFloat(inflation);
    const tValue = parseFloat(time);

    if (isNaN(p) || isNaN(rPercent) || isNaN(tValue) || isNaN(inflationPercent)) {
      setResult(null);
      return;
    }

    const r = rPercent / 100; // Convert nominal rate to decimal
    const pi = inflationPercent / 100; // Convert inflation rate to decimal
    const t = timeUnit === 'years' ? tValue : tValue / 12; // Convert time to years if needed

    if (p <= 0 || t <= 0) {
      setResult(null);
      return;
    }

    let finalAmount = 0;

    switch (interestType) {
      case 'simple':
        finalAmount = p * (1 + r * t);
        break;
      case 'compound':
        finalAmount = p * Math.pow(1 + r / compoundingFrequency, compoundingFrequency * t);
        break;
      case 'continuous':
        finalAmount = p * Math.exp(r * t);
        break;
    }

    const totalInterest = finalAmount - p;

    // Real values calculation
    const realRate = ((1 + r) / (1 + pi)) - 1;
    const realFinalAmount = finalAmount / Math.pow(1 + pi, t);
    const realTotalInterest = realFinalAmount - p;

    setResult({ finalAmount, totalInterest, principal: p, realRate, realFinalAmount, realTotalInterest });
  };

  const interestTypeTabs: { id: InterestType; label: string }[] = [
    { id: 'simple', label: 'Simple' },
    { id: 'compound', label: 'Compuesto' },
    { id: 'continuous', label: 'Continuo' },
  ];

  const activeTabClasses = 'bg-content text-white';
  const inactiveTabClasses = 'bg-base-300 hover:bg-opacity-70 text-gray-300';

  const formattedResult = useMemo(() => {
    if (!result) return null;
    const currencyFormatter = new Intl.NumberFormat('es-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    });
    const percentFormatter = new Intl.NumberFormat('es-US', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
    return {
      finalAmount: currencyFormatter.format(result.finalAmount),
      totalInterest: currencyFormatter.format(result.totalInterest),
      principal: currencyFormatter.format(result.principal),
      realRate: percentFormatter.format(result.realRate),
      realFinalAmount: currencyFormatter.format(result.realFinalAmount),
      realTotalInterest: currencyFormatter.format(result.realTotalInterest),
    };
  }, [result]);

  return (
    <div className="bg-base-200 rounded-2xl shadow-2xl p-6 md:p-8 backdrop-blur-sm bg-opacity-80">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form Section */}
        <div className="flex flex-col space-y-6">
          <div className="bg-base-300 rounded-lg p-1 flex space-x-1">
            {interestTypeTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setInterestType(tab.id)}
                className={`w-full py-2.5 text-sm font-semibold rounded-md transition-all duration-300 ${interestType === tab.id ? activeTabClasses : inactiveTabClasses}`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Monto Principal ($)</label>
            <input
              type="number"
              value={principal}
              onChange={(e) => setPrincipal(e.target.value)}
              className="w-full bg-base-300 border-2 border-transparent focus:border-brand-primary text-white rounded-lg p-3 outline-none transition duration-300"
              placeholder="Ej: 1000"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Tasa de Interés Nominal (%)</label>
              <input
                type="number"
                value={rate}
                onChange={(e) => setRate(e.target.value)}
                className="w-full bg-base-300 border-2 border-transparent focus:border-brand-primary text-white rounded-lg p-3 outline-none transition duration-300"
                placeholder="Ej: 5"
              />
            </div>
             <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Tasa de Inflación Anual (%)</label>
              <div className="relative flex items-center">
                 <input
                    type="number"
                    value={inflation}
                    onChange={(e) => setInflation(e.target.value)}
                    className="w-full bg-base-300 border-2 border-transparent focus:border-brand-primary text-white rounded-lg p-3 pr-10 outline-none transition duration-300"
                    placeholder="Ej: 3"
                />
                <button
                    onClick={fetchInflationRate}
                    disabled={isLoadingInflation}
                    className="absolute right-3 text-gray-400 hover:text-brand-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    aria-label="Obtener inflación de España (INE)"
                    title="Obtener inflación de España (INE)"
                >
                    {isLoadingInflation ? <SpinnerIcon /> : <SyncIcon />}
                </button>
              </div>
            </div>
          </div>
           <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Período de Tiempo</label>
              <div className="flex">
                <input
                  type="number"
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                  className="w-full bg-base-300 border-2 border-transparent focus:border-brand-primary text-white rounded-l-lg p-3 outline-none transition duration-300"
                  placeholder="Ej: 10"
                />
                <select
                  value={timeUnit}
                  onChange={(e) => setTimeUnit(e.target.value as TimeUnit)}
                  className="bg-base-300 text-white rounded-r-lg p-3 border-l-2 border-base-200 outline-none cursor-pointer"
                >
                  <option value="years">Años</option>
                  <option value="months">Meses</option>
                </select>
              </div>
            </div>
          
          {interestType === 'compound' && (
            <div className="transition-opacity duration-500">
              <label className="flex items-center text-sm font-medium text-gray-300 mb-2">
                Frecuencia de Capitalización
                <span className="ml-2 group relative">
                  <InfoIcon />
                  <span className="absolute bottom-full mb-2 w-48 hidden group-hover:block bg-base-100 text-white text-xs rounded-lg py-2 px-3 shadow-lg">
                    Con qué frecuencia se calcula y se suma el interés al principal.
                  </span>
                </span>
              </label>
              <select
                value={compoundingFrequency}
                onChange={(e) => setCompoundingFrequency(parseInt(e.target.value))}
                className="w-full bg-base-300 border-2 border-transparent focus:border-brand-primary text-white rounded-lg p-3 outline-none transition duration-300 cursor-pointer"
              >
                {compoundingOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          )}

          <button
            onClick={handleCalculate}
            className="w-full bg-content text-white font-bold py-3 px-4 rounded-lg hover:bg-opacity-90 transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            Calcular
          </button>
        </div>
        
        {/* Result Section */}
        <div className="flex items-center justify-center">
          {formattedResult ? (
            <ResultCard result={formattedResult} />
          ) : (
            <div className="text-center text-gray-400 p-8 border-2 border-dashed border-base-300 rounded-lg">
                <h3 className="text-lg font-semibold">Tus resultados aparecerán aquí</h3>
                <p className="mt-2 text-sm">Ingresa los datos y haz clic en "Calcular" para ver la magia.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InterestCalculator;