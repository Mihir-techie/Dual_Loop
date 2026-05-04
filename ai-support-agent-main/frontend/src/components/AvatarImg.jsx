export function userAvatarUrl(seed) {
  const s = encodeURIComponent(seed || "user");
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=${s}&backgroundColor=b6e3f4,c0aede,d1d4f9,ffd5dc,ffdfbf`;
}

export function agentAvatarUrl() {
  return "https://api.dicebear.com/7.x/bottts/svg?seed=CognitiveAgent&backgroundColor=0f172a";
}

export default function AvatarImg({ seed, size = 40, isAgent }) {
  const src = isAgent ? agentAvatarUrl() : userAvatarUrl(seed);
  return (
    <img
      src={src}
      width={size}
      height={size}
      alt=""
      className="avatar-img"
      loading="lazy"
    />
  );
}
