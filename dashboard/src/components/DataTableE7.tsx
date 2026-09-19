import { e7FullTable } from "@/data/etapas";

/** Full 27-variable MDI vs. permutation-importance table, collapsed behind <details>. */
export default function DataTableE7() {
  return (
    <details style={{ marginTop: 18 }}>
      <summary style={{ cursor: "pointer", fontSize: 13, color: "var(--muted)" }}>
        Ver las 27 variables completas (MDI vs. permutación)
      </summary>
      <div className="datatable-wrap" style={{ marginTop: 10 }}>
        <table className="datatable">
          <thead>
            <tr>
              <th>Variable</th>
              <th>MDI</th>
              <th>Permutación</th>
              <th>Rank MDI</th>
              <th>Rank perm.</th>
              <th>Cambio</th>
            </tr>
          </thead>
          <tbody>
            {e7FullTable.map((row) => {
              const delta = row.rankMdi - row.rankPerm;
              return (
                <tr key={row.name}>
                  <td>{row.name}</td>
                  <td className="tabular">{row.mdi.toFixed(4)}</td>
                  <td className="tabular">{row.perm.toFixed(4)}</td>
                  <td className="tabular">{`#${row.rankMdi}`}</td>
                  <td className="tabular">{`#${row.rankPerm}`}</td>
                  <td>
                    {delta > 0 ? (
                      <span className="badge up">{`▲ ${delta}`}</span>
                    ) : delta < 0 ? (
                      <span className="badge down">{`▼ ${Math.abs(delta)}`}</span>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </details>
  );
}
