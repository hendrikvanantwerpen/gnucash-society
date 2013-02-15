SoSalsa Finance GUI
===================

 ! Cannot be run at the same time as GnuCash itself.

 * Account checkup
   - Number of open lots (bills/invoices)
   - Free splits in accounts where reconciliation & lots are expected (A/R, A/P, Deposits)
   - Number of unposted invoices/bills
   ? Lots in accounts where it's not expected
   ? profit and loss + budget generation
   ? Tussenrekeningen not zero.

 * Taxes
   + Create accompanying lot in A/R or A/P
   + Generate aangifte transaction
   + Tax period (defaults to previous month)
   + Amounts in all tax categories
   + Generate detailed BTW report as well.

 * Bank
   ? Manually add lines
   ? Payment reminder by email
   + Payable : all unreconciled splits (exclude payments to the account) or open lots in A/P + overpaid lots in A/R.
   + Receivables : all unreconciled splits (exclude charges from the account) or open lots in A/R + overcharged lots in A/R.
   + Select lines for inclusion.
   + Easily select contact for payment.
   + Set account holder & number from selected contact
   + If lot prefill info from bill/invoice if available.
   + Generate clieop, add note to invoice/bill if any.

 * Mass invoices
   + Input invoice lines (desc, account, amount, taxes)
   + Select contacts for which to generate such invoice.

 * Members
   + Select exported CSV from CiviCRM to import.
   + Allow mapping of columns on fields

 * Backup
   ? After backup, delete gnucash logs
   ? Show list of backups
   ? allow restore of a single file to a different filename then the original.

 * Maybe budget + report
 * Maybe book closing

 @ Settings
   - Reconciliable accounts[]
   - Tax accounts
   ? Email settings
   + Gnucash install location
   + Gnucash file

Holy grail
==========

These extensions become accessible from a gnucash menu item. Maybe they
could even integrate screens from gtk python, having no seperate feeling
for everything.
