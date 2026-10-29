/* Reserve a conservative My Paper-only daily budget before every provider
   attempt. This does not measure or guarantee capacity for other projects. */
export async function reserveSend(query,kind='confirmation') {
 if(!['confirmation','digest'].includes(kind)) throw new Error('invalid budget');
 const rows=await query(`INSERT INTO briefing.send_budget_v2(day,kind,used)
   VALUES ((now() AT TIME ZONE 'UTC')::date,$1,1)
   ON CONFLICT (day,kind) DO UPDATE SET used=briefing.send_budget_v2.used+1
   WHERE briefing.send_budget_v2.used < CASE WHEN $1='confirmation' THEN 40 ELSE 100 END RETURNING used`,[kind]);
 return rows.length===1;
}
