import Head from 'next/head';
import SpiralView from '../components/SpiralView';
import WellChat from '../components/WellChat';
import DocumentSearch from '../components/DocumentSearch';
import WellOverview from '../components/WellOverview';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-4">
      <Head>
        <title>Show Me the Well</title>
      </Head>
      <h1 className="text-2xl font-bold mb-4">Show Me the Well</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-4">
          <SpiralView wellId="WELL-001" />
          <DocumentSearch wellId="WELL-001" />
        </div>
        <div className="space-y-4">
          <WellChat wellId="WELL-001" />
          <WellOverview wellId="WELL-001" />
        </div>
      </div>
    </div>
  );
}
