/**
 * Typed API client for Engineering Memory.
 *
 * All methods throw on non-2xx responses, surfacing the `detail` field
 * from the FastAPI error body as the error message.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
const TOKEN_KEY = "em_access_token";

// ---------------------------------------------------------------------------
// Low-level fetch helper
// ---------------------------------------------------------------------------

async function apiFetch<T>(
  path: string,
  options: RequestInit & { orgSlug?: string } = {},
): Promise<T> {
  const { orgSlug, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(fetchOptions.headers as Record<string, string>),
  };

  const token =
    typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (orgSlug) {
    headers["X-Org-Slug"] = orgSlug;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const err = await response.json();
      message = err?.detail ?? message;
    } catch {
      // ignore parse errors
    }
    throw new Error(message);
  }

  // 204 No Content
  if (response.status === 204) {
    return undefined as unknown as T;
  }

  return response.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface UserResponse {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export interface OrgResponse {
  id: string;
  name: string;
  slug: string;
  plan: string;
  is_active: boolean;
  created_at: string;
}

export interface MemberResponse {
  id: string;
  user_id: string;
  organization_id: string;
  role: string;
  created_at: string;
  user_email: string | null;
  user_full_name: string | null;
}

export interface OrgWithMembershipResponse {
  organization: OrgResponse;
  membership: MemberResponse;
}

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------

export const authApi = {
  async register(payload: {
    email: string;
    password: string;
    full_name?: string;
  }): Promise<TokenResponse> {
    const data = await apiFetch<TokenResponse>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    return data;
  },

  async login(payload: {
    email: string;
    password: string;
  }): Promise<TokenResponse> {
    const data = await apiFetch<TokenResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    return data;
  },

  async me(): Promise<UserResponse> {
    return apiFetch<UserResponse>("/api/v1/auth/me");
  },

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
  },

  getToken(): string | null {
    return typeof window !== "undefined"
      ? localStorage.getItem(TOKEN_KEY)
      : null;
  },

  isAuthenticated(): boolean {
    return !!authApi.getToken();
  },
};

// ---------------------------------------------------------------------------
// Organisation API
// ---------------------------------------------------------------------------

export const orgApi = {
  async create(payload: {
    name: string;
    slug: string;
    plan?: string;
  }): Promise<OrgWithMembershipResponse> {
    return apiFetch<OrgWithMembershipResponse>("/api/v1/organizations", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async get(slug: string): Promise<OrgResponse> {
    return apiFetch<OrgResponse>(`/api/v1/organizations/${slug}`, {
      orgSlug: slug,
    });
  },

  async listMembers(slug: string): Promise<MemberResponse[]> {
    return apiFetch<MemberResponse[]>(`/api/v1/organizations/${slug}/members`, {
      orgSlug: slug,
    });
  },

  async addMember(
    slug: string,
    payload: { email: string; role?: string },
  ): Promise<MemberResponse> {
    return apiFetch<MemberResponse>(`/api/v1/organizations/${slug}/members`, {
      method: "POST",
      body: JSON.stringify(payload),
      orgSlug: slug,
    });
  },

  async removeMember(slug: string, userId: string): Promise<void> {
    return apiFetch<void>(`/api/v1/organizations/${slug}/members/${userId}`, {
      method: "DELETE",
      orgSlug: slug,
    });
  },
};

// ---------------------------------------------------------------------------
// Digest API
// ---------------------------------------------------------------------------

export interface DigestResponse {
  id: string;
  digest_type: string;
  period_start: string;
  period_end: string;
  created_at: string;
  markdown_content?: string;
  structured_data?: Record<string, unknown>;
}

export const digestApi = {
  async list(limit: number = 10): Promise<DigestResponse[]> {
    return apiFetch<DigestResponse[]>(`/api/v1/digests?limit=${limit}`);
  },

  async get(id: string): Promise<DigestResponse> {
    return apiFetch<DigestResponse>(`/api/v1/digests/${id}`);
  },

  async generate(periodType: "daily" | "weekly"): Promise<DigestResponse> {
    return apiFetch<DigestResponse>("/api/v1/digests/generate", {
      method: "POST",
      body: JSON.stringify({ period_type: periodType }),
    });
  },
};

// ---------------------------------------------------------------------------
// Release API
// ---------------------------------------------------------------------------

export interface ReleaseResponse {
  id: string;
  start_tag_name: string;
  end_tag_name: string;
  start_date: string;
  end_date: string;
  created_at: string;
  markdown_content?: string;
  structured_data?: Record<string, unknown>;
}

export const releaseApi = {
  async list(limit: number = 10): Promise<ReleaseResponse[]> {
    return apiFetch<ReleaseResponse[]>(`/api/v1/releases?limit=${limit}`);
  },

  async get(id: string): Promise<ReleaseResponse> {
    return apiFetch<ReleaseResponse>(`/api/v1/releases/${id}`);
  },

  async generate(payload: {
    start_tag_name: string;
    end_tag_name: string;
    start_date: string;
    end_date: string;
  }): Promise<ReleaseResponse> {
    return apiFetch<ReleaseResponse>("/api/v1/releases/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};



// ---------------------------------------------------------------------------
// Search API
// ---------------------------------------------------------------------------

export interface SearchResult {
  id: string;
  repository: string;
  pr_number: number;
  title: string;
  author: string;
  merged_at: string | null;
  risk_level: string;
  summary: string;
  engineering_impact: string;
}

export const searchApi = {
  async search(q: string, limit = 10): Promise<{ results: SearchResult[] }> {
    return apiFetch<{ results: SearchResult[] }>(
      `/api/v1/search?q=${encodeURIComponent(q)}&limit=${limit}`
    );
  },
};

// ---------------------------------------------------------------------------
// Assistant API
// ---------------------------------------------------------------------------

export const assistantApi = {
  async ask(question: string): Promise<{ answer: string }> {
    return apiFetch<{ answer: string }>("/api/v1/assistant/ask", {
      method: "POST",
      body: JSON.stringify({ question }),
    });
  },
};
