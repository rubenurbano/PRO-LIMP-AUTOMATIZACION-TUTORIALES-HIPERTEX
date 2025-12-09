
import React from 'react';

interface FormattedResult {
    finalAmount: string;
    totalInterest: string;
    principal: string;
    realRate: string;
    realFinalAmount: string;
    realTotalInterest: string;
}

interface ResultCardProps {
  result: FormattedResult;
}

const ResultCard: React.FC<ResultCardProps> = ({ result }) => {
  const isRealRateNegative = result.realRate.startsWith('-');
  const isRealInterestNegative = result.realTotalInterest.startsWith('-');

  return (
    <div className="w-full bg-gradient-to-tl from-base-300 to-base-200 rounded-xl shadow-lg p-6 space-y-4 animate-fade-in">
        <div className="text-center mb-4">
            <p className="text-sm text-gray-400">Monto Final (Nominal)</p>
            <p className="text-4xl font-bold text-brand-primary tracking-wider">{result.finalAmount}</p>
        </div>
        
        <div className="space-y-2 text-lg">
            <div className="flex justify-between items-center">
                <span className="text-gray-300">Monto Principal:</span>
                <span className="font-semibold text-white">{result.principal}</span>
            </div>
            <div className="flex justify-between items-center">
                <span className="text-gray-300">Interés Total Ganado:</span>
                <span className="font-semibold text-green-400">{result.totalInterest}</span>
            </div>
        </div>
        
        <div className="border-t border-base-100 my-4 opacity-50"></div>

        <div className="text-center mb-4">
            <p className="text-sm text-gray-400">Poder Adquisitivo Final (Real)</p>
            <p className="text-3xl font-bold text-white tracking-wider">{result.realFinalAmount}</p>
        </div>
        
        <div className="space-y-2 text-lg">
             <div className="flex justify-between items-center">
                <span className="text-gray-300">Tasa Real de Interés:</span>
                <span className={`font-semibold ${isRealRateNegative ? 'text-red-400' : 'text-green-400'}`}>{result.realRate}</span>
            </div>
            <div className="flex justify-between items-center">
                <span className="text-gray-300">Ganancia Real:</span>
                <span className={`font-semibold ${isRealInterestNegative ? 'text-red-400' : 'text-green-400'}`}>{result.realTotalInterest}</span>
            </div>
        </div>
    </div>
  );
};

export default ResultCard;
