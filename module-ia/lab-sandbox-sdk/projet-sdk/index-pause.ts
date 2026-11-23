// Variante du lab S12 : le sandbox reste vivant 60 secondes avant sa suppression,
// pour pouvoir le voir avec « sbx --cloud ls » dans un autre terminal.
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
    { args: ['uname', '-a'] },
    { timeoutMs: 300_000 },
  );
  console.log(result.stdout.trim());

  console.log('Pause de 60 secondes : lancez « sbx --cloud ls » dans un autre terminal.');
  await new Promise((resolve) => setTimeout(resolve, 60_000));

  const latest = await sandbox.refresh();
  const deleting = await latest.delete({ force: true });
  await deleting?.waitUntilDeleted();
  console.log('Supprimé :', sandbox.name);
} finally {
  await client.close();
}
