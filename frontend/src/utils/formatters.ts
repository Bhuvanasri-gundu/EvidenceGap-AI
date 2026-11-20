/**
 * Scientific formatters for EvidenceGap AI.
 */

export function formatPmidUrl(pmid: string | number): string {
  const clean = String(pmid).replace(/[^0-9]/g, '');
  return `https://pubmed.ncbi.nlm.nih.gov/${clean}/`;
}

export function formatPmcUrl(pmcid: string): string {
  const clean = pmcid.startsWith('PMC') ? pmcid : `PMC${pmcid}`;
  return `https://www.ncbi.nlm.nih.gov/pmc/articles/${clean}/`;
}

export function formatScorePercent(score: number | null | undefined): string {
  if (score === null || score === undefined || isNaN(score)) return '0%';
  return `${Math.round(score * 100)}%`;
}

export function formatRelativeDate(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

export function truncateText(text: string, maxLength: number = 160): string {
  if (!text || text.length <= maxLength) return text;
  return `${text.slice(0, maxLength).trim()}...`;
}
