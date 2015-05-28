import MySQLdb as mdb

class Database:
    def __init__(self):
        try:
            self.connection = mdb.connect('localhost', 'root', 'raspberry', 'sklad');
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1]);
    def getFirstCommand(self):
        self.__init__();
        cur = self.connection.cursor();
        cur.execute("SELECT * FROM `queue` ORDER BY id ASC;");
        try:
            return cur.fetchone();
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1]);
            return None;
        cur.close()
    def moveCommand(self, commandId, state):
        cur = self.connection.cursor();
        cur.execute("SELECT * FROM `queue` WHERE `id` = %d" % (commandId));
        row = cur.fetchone();
        print row;
        queue = "INSERT INTO `history` VALUES(%d, %d, %d, %d, %d, %d, %d, %d);" % (row[0], state, int(row[2].strftime("%s")), row[3], row[4], row[5], row[6], row[7]);
        print queue;
        cur.execute(queue);

        queue = "SELECT amount FROM `partitions` WHERE `id` = %d" % (row[5]);
        cur.execute(queue);
        oldAmount = cur.fetchone()[0];

        queue = "UPDATE `partitions` SET `amount` = %d WHERE `id` = %d" % (oldAmount - row[6], row[5]);
        cur.execute(queue);

        queue = "DELETE FROM `queue` WHERE id = %d;" % (commandId);
        print queue;
        cur.execute(queue);
        self.connection.commit();
        cur.close();
