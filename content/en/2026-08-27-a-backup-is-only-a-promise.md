---
slug: a-backup-is-only-a-promise
title: A Backup Is Only a Promise Until You Restore It
dek: A green checkmark proves that something was copied. A small restore test proves
  that the copy can still help you.
section: tech
type: analysis
depth: open
lang: en
date: '2026-08-27'
status: published
confidence: 95
load: 0
topics: []
automation_generated: true
edition_slot: 3
automation_role: edition
generator: chatgpt-work
format: ''
event_id: ''
series: ''
image_query: conceptual archive box with one recovered family photo and document no
  logos
sources:
- name: NIST SP 800-184 — Guide for Cybersecurity Event Recovery
  url: https://csrc.nist.gov/pubs/sp/800/184/final
  published: 2016-12
- name: UK National Cyber Security Centre — Mitigating malware and ransomware attacks
  url: https://www.ncsc.gov.uk/guidance/mitigating-malware-and-ransomware-attacks
  published: '2020-02-13'
- name: UK National Cyber Security Centre — Ransomware-resistant cloud backups
  url: https://www.ncsc.gov.uk/collection/ransomware-resistant-backups/principles-for-ransomware-resistant-cloud-backups
  published: '2024-11-22'
- name: Apple Support — Back up your Mac with Time Machine
  url: https://support.apple.com/en-us/104984
  published: '2026-07-06'
- name: Apple Support — Restore your Mac from a backup
  url: https://support.apple.com/en-asia/102551
  published: '2025-11-10'
qma_path: ''
tickers: []
quiz:
  question: What does a successful small restore test prove that a “backup completed”
    message does not?
  options:
  - That the copied data can be found, opened and used
  - That every future backup will be perfect
  - That ransomware cannot reach any device
  answer: 0
  explanation: A restore test checks recoverability of selected data. It cannot guarantee
    future jobs or eliminate other security risks.
---

## BRIEFLY

**What happened.** Phones, laptops and cloud services make copying data feel automatic, yet a completed backup job is not the same thing as a recoverable file.

**What it means.** A green checkmark confirms a process reported success. It does not prove that the right folders were included, an older version still exists, the encryption password is available, or the restored file will open.

**Risks and impact.** People often discover missing folders, expired retention, damaged media or lost credentials only after theft, hardware failure, accidental deletion or ransomware.

**What can be done.** Run a small, non-destructive restore drill: choose representative files, restore them to a separate folder, open them, record how long it took and fix the first failure.

**What to watch.** Check scope, age, version history, separation from the original device, access credentials and the date of the last successful restore—not merely the last backup.

## FACTS

The direct answer is simple: you do not know that a backup works until you retrieve something from it and use it.

Backup software normally performs a copy operation on a schedule. It may report that the job finished, how many files it processed and when it last connected. Those are useful signals. They say little about whether the copy contains the file you care about or whether you can recover it under realistic conditions.

Three tools are commonly confused. Synchronisation keeps working folders aligned across devices. That is convenient, but a deletion or corrupted file may also synchronise. Version history preserves earlier states for a retention period. A backup keeps a separate recovery copy according to its own schedule and rules. Some services combine all three; the label alone does not tell you which failure they survive.

Apple's Time Machine documentation illustrates both the convenience and the boundary. It makes hourly, daily and weekly copies, then removes the oldest when the disk fills. It can restore individual files or migrate a wider account. The mechanism is useful precisely because it has a restore path. Its schedule is not a promise that every external drive, cloud folder or excluded location was included.

## EVIDENCE

NIST's Guide for Cybersecurity Event Recovery treats recovery as a planned capability, not a final button pressed after damage. The point is broader than ransomware: an organisation needs to know what must be restored, in what order, with which people, systems and dependencies available.

The UK's National Cyber Security Centre makes the operational lesson explicit. Its malware guidance recommends regular backups, multiple copies in different locations and regular tests that confirm files can be restored. It also warns against leaving removable backup devices permanently connected, because attackers may target accessible copies.

Newer NCSC principles explain why a backup can be present and still fail. An attacker may delete it, alter retention rules, corrupt successive versions or remove the accounts needed to reach it. The guidance therefore calls for protected version history, monitoring, independent access routes and on-demand restore testing.

These documents are written largely for organisations, but the household version is recognisable. If the only copy sits on a drive always attached to the infected laptop, it is not well separated. If the only recovery password is stored on the lost phone, access is circular. If a photo library was excluded without anyone noticing, a successful job protected the wrong thing.

## PERSPECTIVES

One response is to automate everything and trust the system. Automation is valuable because memory is unreliable. It prevents the familiar plan to “do a backup this weekend” from ageing into folklore. But automation can repeat a mistake perfectly: the wrong folder, a full disk, a disconnected account or a retention window shorter than expected.

The opposite response is to make several manual copies. That can create separation, yet hand-made copies are easy to postpone and hard to inventory. Several folders called “final” on one drive are not several independent backups.

A third view says cloud storage has made local testing obsolete. Cloud services can protect against a broken laptop and may retain old versions. They also depend on account access, provider rules and the distinction between sync and backup. The sensible conclusion is not cloud bad or hard drive good. It is that recovery should not depend on the same single event destroying the original.

No home drill can prove that every file and every disaster is covered. A restored document today does not guarantee that next month's job will run. Testing reduces uncertainty; it does not abolish it.

## CONTEXT

Recovery has two clocks. The first is the age of the newest usable copy: how much recent work could be lost? The second is the time needed to get working again: minutes for one document, hours for a photo library, perhaps days for a complete computer.

These clocks explain why “I have a backup” is incomplete. A monthly copy may be adequate for an archive that rarely changes and poor for a daily project. A perfect copy may still be impractical if it requires a password nobody can find or a connection that is unavailable during an outage.

Retention matters too. Apple's published Time Machine schedule keeps progressively fewer historical points and deletes the oldest copies as space fills. Cloud services also use retention rules. If damage goes unnoticed long enough, clean versions may age out while corrupted or encrypted files keep arriving.

A restore test should therefore imitate a small part of the failure without creating one. Do not erase the original device to prove courage. Recover selected files to a separate destination and compare the result.

## DEEPER

Try this 20-minute restore audit.

First, choose four representative items: a recent document, an older photo, a folder containing several files and one file from a location you are not certain is protected. Avoid using your only copy of anything as the experiment.

Second, write down what you expect. Which service or drive holds each item? How old should the available versions be? What credential or encryption password will you need? This prediction is important because a test that finds only what you already know to be easy can provide false comfort.

Third, restore to a new folder rather than over the live file. Open the document, view the photo and inspect the folder structure. A filename in a catalogue is not enough. If practical, compare file sizes or checksums; for most households, simply opening representative files is already much better than trusting a status icon.

Fourth, record four facts: the test date, the newest usable backup, the oldest useful version and the time required. Note any excluded folders, missing passwords or confusing instructions.

Finally, fix one weakness. Connect the scheduled drive. Add the missing folder. Store the recovery key somewhere physically protected and independent of the daily device. Add a second location for irreplaceable material. Then set a modest repeat date—after a major device change and periodically thereafter.

If the data belongs to an employer, school or regulated service, follow its recovery process rather than moving copies into a personal account. A household audit should improve recoverability without creating a new privacy problem.

## REFLECT

A backup is a promise made by yesterday to a future version of you having a very bad morning. The kindest way to check that promise is not to wait for the morning.

Which four files would tell you, quickly and honestly, whether your recovery plan is real?
