import {
  alerts as mockAlerts,
  churnRiskTrend as mockTrend,
  companies as mockCompanies,
  integrationStatus as mockIntegrations,
  riskDistribution as mockDistribution,
  xaiData as mockXai,
} from '../data/mockData';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true';

/**
 * Gecikme Simülasyonu
 */
const delay = (data) =>
  new Promise((resolve) => {
    window.setTimeout(() => resolve(data), 180);
  });

/**
 * Merkezi JSON İsteği Fonksiyonu
 * Tüm isteklerin başına otomatik /api/v1 ekler ve hataları yakalar.
 */
async function requestJson(path, options = {}) {
  // Eğer path zaten v1 içermiyorsa ekle
  const fullPath = path.startsWith('/api/v1') ? path : `/api/v1${path}`;
  
  try {
    const response = await fetch(`${API_BASE_URL}${fullPath}`, options);

    if (!response.ok) {
      const errorBody = await response.text().catch(() => '');
      console.error(`API Hatası [${response.status}]:`, errorBody);
      throw new Error(`API Hatası (${response.status}): ${fullPath}`);
    }

    return await response.json();
  } catch (error) {
    console.error("İstek sırasında bir ağ hatası oluştu:", error);
    throw error;
  }
}

// ==========================================
// 1. DASHBOARD SERVİSLERİ
// ==========================================

export async function getDashboardSummary() {
  if (USE_MOCK_DATA) {
    return delay({
      total_clients: 7044,
      high_risk_count: 808,
      medium_risk_count: 1204,
      low_risk_count: 5032,
      revenue_at_risk: 65931.0,
      average_health_score: 80.5,
      last_sync: 'Just now',
    });
  }
  // Backend: GET /api/v1/dashboard/summary
  return requestJson('/dashboard/summary');
}

export async function getChurnRiskTrend() {
  if (USE_MOCK_DATA) return delay(mockTrend);
  // Backend: GET /api/v1/dashboard/trend (404 hatasını önlemek için sabitlendi)
  return requestJson('/dashboard/trend');
}

export async function getRiskDistribution() {
  if (USE_MOCK_DATA) return delay(mockDistribution);
  // Backend: GET /api/v1/dashboard/distribution
  return requestJson('/dashboard/distribution');
}

// ==========================================
// 2. MÜŞTERİ VE CHURN ANALİTİĞİ
// ==========================================

export async function getCustomers() {
  if (USE_MOCK_DATA) return delay(mockCompanies);
  // Backend: GET /api/v1/customers
  return requestJson('/customers');
}

/**
 * Tek bir müşterinin detaylarını çeker. 
 * ID artık String olduğu için Number(id) dönüşümü kaldırıldı.
 */
export async function getCustomerById(id) {
  if (USE_MOCK_DATA) {
    return delay(mockCompanies.find((c) => String(c.company_id) === String(id)));
  }
  // Backend: GET /api/v1/customers/{id}
  return requestJson(`/customers/${id}`);
}

/**
 * Müşteriye özel XAI (SHAP) faktörlerini çeker.
 * View XAI sayfasının boş kalmaması için bu endpoint kritiktir.
 */
export async function getCustomerXai(id) {
  if (USE_MOCK_DATA) {
    return delay(mockXai.find((item) => String(item.company_id) === String(id)));
  }
  // Backend: GET /api/v1/customers/{id}/xai
  return requestJson(`/customers/${id}/xai`);
}

/**
 * Müşterinin kullanım trendini (grafik) çeker.
 */
export async function getCustomerUsageTrend(id) {
  if (USE_MOCK_DATA) {
    const company = mockCompanies.find((c) => String(c.company_id) === String(id));
    return delay(company?.usage_trend || []);
  }
  // Backend: GET /api/v1/customers/{id}/usage
  return requestJson(`/customers/${id}/usage`);
}

// ==========================================
// 3. ALERTLER VE SİSTEM DURUMU
// ==========================================

export async function getAlerts() {
  if (USE_MOCK_DATA) return delay(mockAlerts);
  // Backend: GET /api/v1/alerts
  return requestJson('/alerts');
}

export async function getIntegrationStatus() {
  if (USE_MOCK_DATA) return delay(mockIntegrations);
  // Backend: GET /api/v1/integrations/status
  return requestJson('/integrations/status');
}

// ==========================================
// 4. RAPORLAMA
// ==========================================

export async function exportChurnRiskCsv() {
  const response = await fetch(`${API_BASE_URL}/api/v1/reports/churn-risk.csv`);
  if (!response.ok) throw new Error("CSV dışa aktarma hatası.");
  return response.text();
}

// ==========================================
// 5. DATA IMPORT
// ==========================================

export async function uploadCsvFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_BASE_URL}/api/v1/import/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: `Upload failed (${response.status})` }));
    throw new Error(err.detail || `Upload failed (${response.status})`);
  }
  return response.json();
}

