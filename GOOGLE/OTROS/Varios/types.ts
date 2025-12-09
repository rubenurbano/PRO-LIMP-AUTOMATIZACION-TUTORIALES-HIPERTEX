
export type InterestType = 'simple' | 'compound' | 'continuous';

export type TimeUnit = 'years' | 'months';

export interface Result {
  finalAmount: number;
  totalInterest: number;
  principal: number;
  realRate: number;
  realFinalAmount: number;
  realTotalInterest: number;
}