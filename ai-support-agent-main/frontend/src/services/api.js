import axios from "axios";
import { API_BASE } from "../config";

const client = axios.create({ baseURL: API_BASE });

export function setAuthToken(token) {
  if (token) {
    client.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete client.defaults.headers.common.Authorization;
  }
}

export async function signup(payload) {
  const res = await client.post("/auth/signup", payload);
  return res.data;
}

export async function login(payload) {
  const res = await client.post("/auth/login", payload);
  return res.data;
}

export async function fetchMe() {
  const res = await client.get("/auth/me");
  return res.data;
}

export async function listConversations() {
  const res = await client.get("/conversations");
  return res.data;
}

export async function createConversation(body = {}) {
  const res = await client.post("/conversations", body);
  return res.data;
}

export async function fetchMessages(conversationId) {
  const res = await client.get(`/conversations/${conversationId}/messages`);
  return res.data;
}

export async function sendChat(conversationId, body) {
  const res = await client.post(`/conversations/${conversationId}/chat`, body);
  return res.data;
}

export async function fetchMemoryOverview() {
  const res = await client.get("/memory/overview");
  return res.data;
}

export async function fetchMemoryGraph() {
  const res = await client.get("/memory/graph");
  return res.data;
}

export async function probeMemory(query) {
  const res = await client.post("/memory/probe", { query });
  return res.data;
}

export async function fetchPersonas() {
  const res = await client.get("/demo/personas");
  return res.data;
}

export async function postFeedback(conversationId, messageId, helpful) {
  const res = await client.post(`/conversations/${conversationId}/feedback`, {
    message_id: messageId,
    helpful,
  });
  return res.data;
}

export { client };
