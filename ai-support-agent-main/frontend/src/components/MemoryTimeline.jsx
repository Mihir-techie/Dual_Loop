const MemoryTimeline = ({ memory }) => {
  return (
    <div style={{
      marginTop: "20px",
      padding: "15px",
      borderRadius: "12px",
      background: "#ffffff",
      boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
    }}>
      <h3 style={{
        marginBottom: "10px",
        textAlign: "center"
      }}>
        🧠 Memory Timeline
      </h3>

      {/* Empty State */}
      {memory.length === 0 && (
        <p style={{ textAlign: "center", color: "#888" }}>
          No memory yet...
        </p>
      )}

      {/* Memory List */}
      <div style={{
        maxHeight: "200px",
        overflowY: "auto"
      }}>
        {memory.map((m, index) => (
          <div key={index} style={{
            padding: "10px",
            marginBottom: "10px",
            borderRadius: "10px",
            background: "#f9f9f9",
            borderLeft: "4px solid #4CAF50"
          }}>
            <p style={{ margin: "5px 0" }}>
              <b>👤 User:</b> {m.user}
            </p>
            <p style={{ margin: "5px 0" }}>
              <b>🤖 Bot:</b> {m.bot}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MemoryTimeline;