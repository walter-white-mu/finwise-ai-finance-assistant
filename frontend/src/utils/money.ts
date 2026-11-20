const amountPattern = /^\d+(?:\.\d{1,2})?$/

export const isPositiveMoney = (value: string): boolean =>
  amountPattern.test(value.trim()) && Number(value) > 0

export const toMinorUnits = (value: string): bigint => {
  const [whole, fraction = ''] = value.split('.')
  return BigInt(whole) * 100n + BigInt(fraction.padEnd(2, '0'))
}

export const formatMinorUnits = (minorUnits: bigint): string => {
  const rupees = Number(minorUnits) / 100
  return new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR', minimumFractionDigits: 2, maximumFractionDigits: 2
  }).format(rupees)
}

export const formatRupees = (amount: string): string =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR', minimumFractionDigits: 2, maximumFractionDigits: 2
  }).format(Number(amount))

export const formatDate = (value: string): string =>
  new Intl.DateTimeFormat('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC'
  }).format(new Date(`${value}T00:00:00Z`))
