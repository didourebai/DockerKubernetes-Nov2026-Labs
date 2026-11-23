// Lab S12 : créer un Cloud Sandbox, exécuter une commande, le supprimer.
// Exemple tiré du tutoriel « Run your first cloud sandbox » de la doc Docker Sandboxes.
import { oauth, Sandboxes } from '@docker/sandboxes';

const client = new Sandboxes({
  auth: oauth({
    onVerification({ verificationUriComplete, verificationUri, userCode }) {
      console.log(`Ouvrez ${verificationUriComplete ?? verificationUri}`);
      console.log(`Code de vérification : ${userCode}`);
    },
  }),
});

try {
  const sandbox = await client.kits.launchAndWait('shell');
  console.log('Sandbox :', sandbox.name);

  const result = await sandbox.processes.run(
    { args: ['echo', 'Bonjour depuis Docker Sandboxes'] },
    { timeoutMs: 300_000 },
  );
  console.log(result.stdout.trim());

  const latest = await sandbox.refresh();
  const deleting = await latest.delete({ force: true });
  await deleting?.waitUntilDeleted();
  console.log('Supprimé :', sandbox.name);
} finally {
  await client.close();
}
