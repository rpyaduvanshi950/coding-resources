import { useMemo, useRef, useState } from 'react';
import { deleteApp, initializeApp } from 'firebase/app';
import { collection, getDocs, getFirestore } from 'firebase/firestore';
import * as XLSX from 'xlsx';

const FIELD_ORDER = [
  'userId',
  'id',
  'name',
  'email',
  'phone',
  'whatsapp',
  'gender',
  'address',
  'teamId',
  'teamName',
  'college',
  'collegeCity',
  'year',
  'fb',
  'insta',
  'isTeamLeader',
  'dateTime',
  'competitions'
];

function formatDocument(docSnapshot) {
  const data = docSnapshot.data() ?? {};
  return {
    userId: docSnapshot.id,
    id: data.id ?? '',
    name: data.name ?? '',
    email: data.email ?? '',
    phone: data.phone ?? '',
    whatsapp: data.whatsapp ?? '',
    gender: data.gender ?? '',
    address: data.address ?? '',
    teamId: data.teamId ?? '',
    teamName: data.teamName ?? '',
    college: data.college ?? '',
    collegeCity: data.collegeCity ?? '',
    year: data.year ?? '',
    fb: data.fb ?? '',
    insta: data.insta ?? '',
    isTeamLeader: data.isTeamLeader ?? '',
    dateTime: data.dateTime ?? '',
    competitions: Array.isArray(data.competitions)
      ? data.competitions.join(', ')
      : ''
  };
}

function App() {
  const [configText, setConfigText] = useState('');
  const [collectionName, setCollectionName] = useState('eventsUsers2025');
  const [documents, setDocuments] = useState([]);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const appRef = useRef(null);

  const columns = useMemo(() => FIELD_ORDER, []);

  const parseFirebaseConfig = () => {
    try {
      const parsed = JSON.parse(configText);
      if (!parsed || typeof parsed !== 'object') {
        throw new Error('The Firebase configuration must be a JSON object.');
      }
      return parsed;
    } catch (error) {
      throw new Error('Unable to parse Firebase config JSON. Please check the syntax.');
    }
  };

  const ensureFirebaseApp = async (config) => {
    if (appRef.current) {
      const existingOptions = appRef.current.options ?? {};
      if (existingOptions.projectId === config.projectId) {
        return appRef.current;
      }
      await deleteApp(appRef.current);
      appRef.current = null;
    }

    const appName = `client-app-${Date.now()}`;
    const app = initializeApp(config, appName);
    appRef.current = app;
    return app;
  };

  const handleFetch = async () => {
    setErrorMessage('');
    setStatusMessage('');
    setIsLoading(true);

    try {
      const trimmedCollection = collectionName.trim();
      if (!trimmedCollection) {
        throw new Error('Collection name cannot be empty.');
      }

      const parsedConfig = parseFirebaseConfig();
      const app = await ensureFirebaseApp(parsedConfig);
      const firestore = getFirestore(app);
      const snapshot = await getDocs(collection(firestore, trimmedCollection));
      const rows = snapshot.docs.map(formatDocument);

      setDocuments(rows);
      setStatusMessage(`Fetched ${rows.length} document${rows.length === 1 ? '' : 's'} from "${trimmedCollection}".`);
    } catch (error) {
      setDocuments([]);
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (!documents.length) {
      setErrorMessage('No data available to export. Fetch data first.');
      return;
    }

    setErrorMessage('');
    const worksheetData = documents.map((row) => {
      const orderedRow = {};
      columns.forEach((column) => {
        orderedRow[column] = row[column] ?? '';
      });
      return orderedRow;
    });

    const worksheet = XLSX.utils.json_to_sheet(worksheetData, { header: columns });
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Firestore Data');

    const fileName = `${collectionName.trim() || 'firestore-data'}.xlsx`;
    XLSX.writeFile(workbook, fileName);
    setStatusMessage(`Excel file "${fileName}" downloaded successfully.`);
  };

  const handleClear = async () => {
    setDocuments([]);
    setStatusMessage('Cleared the current dataset.');
    setErrorMessage('');
    if (appRef.current) {
      await deleteApp(appRef.current);
      appRef.current = null;
    }
  };

  const handleConfigSample = () => {
    setConfigText(
      JSON.stringify(
        {
          apiKey: 'YOUR_API_KEY',
          authDomain: 'YOUR_PROJECT_ID.firebaseapp.com',
          projectId: 'YOUR_PROJECT_ID',
          storageBucket: 'YOUR_PROJECT_ID.appspot.com',
          messagingSenderId: 'YOUR_SENDER_ID',
          appId: 'YOUR_APP_ID'
        },
        null,
        2
      )
    );
  };

  return (
    <div className="app-container">
      <header>
        <h1>Firebase Collection Exporter</h1>
        <p>
          Paste your web Firebase configuration, specify the Firestore collection, then fetch and
          download the data as an Excel spreadsheet.
        </p>
      </header>

      <section className="card">
        <div className="field">
          <label htmlFor="config">Firebase config (JSON)</label>
          <textarea
            id="config"
            value={configText}
            onChange={(event) => setConfigText(event.target.value)}
            placeholder={`{\n  "apiKey": "...",\n  "authDomain": "..."\n}`}
            rows={12}
          />
          <button type="button" className="secondary" onClick={handleConfigSample}>
            Fill with sample structure
          </button>
        </div>

        <div className="field">
          <label htmlFor="collection">Collection name</label>
          <input
            id="collection"
            type="text"
            value={collectionName}
            onChange={(event) => setCollectionName(event.target.value)}
            placeholder="eventsUsers2025"
          />
        </div>

        <div className="actions">
          <button type="button" onClick={handleFetch} disabled={isLoading}>
            {isLoading ? 'Fetching…' : 'Fetch collection'}
          </button>
          <button type="button" onClick={handleDownload} disabled={!documents.length}>
            Download Excel
          </button>
          <button type="button" className="secondary" onClick={handleClear}>
            Reset
          </button>
        </div>
      </section>

      {(statusMessage || errorMessage) && (
        <section className="feedback">
          {statusMessage && <div className="status">✅ {statusMessage}</div>}
          {errorMessage && <div className="error">⚠️ {errorMessage}</div>}
        </section>
      )}

      <section className="card">
        <div className="table-header">
          <h2>Preview ({documents.length})</h2>
          <span>Showing up to the first 50 rows.</span>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {documents.length === 0 ? (
                <tr>
                  <td colSpan={columns.length} className="empty">
                    No data loaded yet.
                  </td>
                </tr>
              ) : (
                documents.slice(0, 50).map((row) => (
                  <tr key={row.userId}>
                    {columns.map((column) => (
                      <td key={column}>{String(row[column] ?? '')}</td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      <footer>
        <p>
          Tip: Use a Firebase Web API key and Firestore security rules that restrict reads to
          authorised users. Avoid exposing admin credentials in client-side applications.
        </p>
      </footer>
    </div>
  );
}

export default App;
