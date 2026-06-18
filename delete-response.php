<?php
/**
 * Smaže právě jeden záznam z tabulky `responses` podle jeho ID.
 *
 * Používá připravený dotaz s vázaným parametrem, takže smaže výhradně
 * jeden konkrétní řádek (nikdy ne víc). Vrací počet skutečně smazaných
 * řádků — 1 pokud záznam existoval, 0 pokud žádný takový záznam nebyl.
 *
 * @param PDO $db  Otevřené spojení do SQLite databáze.
 * @param int $id  ID záznamu ke smazání.
 * @return int     Počet smazaných řádků (0 nebo 1).
 */
function deleteResponseById(PDO $db, int $id): int {
    $stmt = $db->prepare('DELETE FROM responses WHERE id = ?');
    $stmt->execute([$id]);
    return $stmt->rowCount();
}
