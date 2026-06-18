<?php
/**
 * Test pro deleteResponseById(): ověřuje, že se maže POUZE jeden
 * konkrétní záznam a žádné další.
 *
 * Spuštění:  php tests/DeleteResponseTest.php
 * Návratový kód 0 = vše prošlo, 1 = test selhal.
 */

require __DIR__ . '/../delete-response.php';

$failures = 0;

function check(bool $cond, string $msg): void {
    global $failures;
    if ($cond) {
        echo "  ✓ $msg\n";
    } else {
        echo "  ✗ $msg\n";
        $failures++;
    }
}

/** Vytvoří čerstvou in-memory DB se 4 záznamy. */
function makeDb(): PDO {
    $db = new PDO('sqlite::memory:');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $db->exec('CREATE TABLE responses (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid       TEXT    UNIQUE NOT NULL,
        data       TEXT,
        email      TEXT,
        status     TEXT    DEFAULT "partial",
        last_page  TEXT,
        created_at TEXT,
        updated_at TEXT
    )');
    $ins = $db->prepare('INSERT INTO responses (uuid, data) VALUES (?, ?)');
    foreach (['aaa', 'bbb', 'ccc', 'ddd'] as $i => $uuid) {
        $ins->execute([$uuid, json_encode(['x' => $i])]);
    }
    return $db;
}

function countRows(PDO $db): int {
    return (int)$db->query('SELECT COUNT(*) FROM responses')->fetchColumn();
}

echo "Test: deleteResponseById smaže právě jeden záznam\n";
$db = makeDb();
check(countRows($db) === 4, 'Připraveny 4 záznamy');

$deleted = deleteResponseById($db, 2);
check($deleted === 1, 'Funkce vrátí počet 1 (smazán právě jeden řádek)');
check(countRows($db) === 3, 'V DB zbyly 3 záznamy (ubyl přesně jeden)');

$remaining = $db->query('SELECT id FROM responses ORDER BY id')->fetchAll(PDO::FETCH_COLUMN);
check($remaining == [1, 3, 4], 'Zůstaly všechny ostatní záznamy (1, 3, 4), smazán jen #2');

echo "\nTest: mazání neexistujícího ID nic neodstraní\n";
$db2 = makeDb();
$deleted2 = deleteResponseById($db2, 999);
check($deleted2 === 0, 'Funkce vrátí 0 pro neexistující ID');
check(countRows($db2) === 4, 'Všechny 4 záznamy zůstaly nedotčené');

echo "\n" . ($failures === 0 ? "VŠE PROŠLO\n" : "SELHALO: $failures kontrol\n");
exit($failures === 0 ? 0 : 1);
