---
slug: how-hackers-attack-municipal-water-systems-and-why-the-utilities-are-s
title: How hackers attack municipal water systems – and why the utilities are so vulnerable
dek: A cybersecurity researcher explains how hackers target small computers that control
  a water system’s tanks, pipes and valves.
section: tech
type: syndicated
depth: open
lang: en
date: '2026-08-10'
status: published
confidence: 100
image_query: How hackers attack municipal water systems
syndicated:
  source: The Conversation — Technology
  author: William Akoto, Assistant Professor of Global Security, American University
    School of International Service
  url: https://theconversation.com/how-hackers-attack-municipal-water-systems-and-why-the-utilities-are-so-vulnerable-288864
  license: CC BY-ND 4.0
  license_url: https://creativecommons.org/licenses/by-nd/4.0/
  attribution: By William Akoto, Assistant Professor of Global Security, American
    University School of International Service. This article is republished from <a
    href="https://theconversation.com">The Conversation</a> under a Creative Commons
    licence. <a href="https://theconversation.com/how-hackers-attack-municipal-water-systems-and-why-the-utilities-are-so-vulnerable-288864">Read
    the original article</a>.
  may_translate: false
  may_edit: false
sources:
- name: The Conversation — Technology
  url: https://theconversation.com/how-hackers-attack-municipal-water-systems-and-why-the-utilities-are-so-vulnerable-288864
---

Hackers tried to break into at least 30 municipal water systems in Minnesota on July 26-27, 2026. Since then, Michigan , New Jersey and several other states have reported similar cyberattacks .

The attackers did not try to infiltrate the computers that utility offices use. Instead, they tried to seize control of small computers in equipment like pumps and valves that deliver drinking water to millions of people.

The utilities countered the attacks by shutting down the control computers and sending personnel out into the field to operate equipment manually. Utility officials have said that water remained safe to drink.

As a scholar who researches cyber conflict , I find that the methods used in these incidents are typical of international cyberattacks . Initial suspicion has fallen on hackers allegedly aligned with Iran , but the U.S. government has yet to attribute the attack to anyone.

How can someone from far away seize control of a water system and possibly shut off the flow or taint the water?

### Controlling the water machinery

There are about 152,000 public drinking water systems in the United States, according to the federal government. A municipality gets its water from lakes, reservoirs, rivers or underground aquifers.

Pumps move water through pipes to a treatment plant that filters and disinfects it. More pumps push the treated water into storage tanks, then through distribution pipes to homes and businesses. The entire system can span many square miles.

The hackers accessed small computers called programmable logic controllers at the water systems that operate all sorts of industrial equipment. The programmable logic controllers read sensors that measure conditions such as water pressure, water chemistry, tank levels and equipment status, and automatically operate pumps, valves and alarms. A household thermostat is a useful comparison: It reads the temperature and tells the heating or cooling system what to do.

The programmable logic controllers also transmit operational data to a utility’s central computer system. Workers use dashboards to monitor the information and send commands back to the controllers. The two-way communications can travel through wired networks, over radio or cellular links, or through internet connections.

Many utilities operate with small staffs, so remote connections allow an employee to monitor a distant pump or tank, receive an alarm after hours or let a vendor diagnose equipment without traveling to every site.

Controllers that use the internet may access it directly, or go through protective firewalls, secure gateways or virtual private networks. Direct access is more vulnerable because there are fewer defensive barriers. A hacker can find a controller by scanning the internet and finding its Internet Protocol, or IP, address, then try a weak or stolen password or exploit a known security flaw.

To reach a controller through a secure gateway or encrypted service, a hacker would have to steal remote-access credentials, or break into the gateway or private network, or get control of an operator’s workstation. The hacker could then use that foothold to reach the controller.

Attempted access can also be part of an intruder’s longer-term strategy to collect information, test defenses or establish entry for a later date.

### How an attack works

Attacks on industrial control systems often follow a familiar sequence. Infiltration often begins with a quiet search for access. Attackers scan internet addresses for controllers, dashboards and outside companies that provide remote access services, looking for targets that are linked directly to the internet.

Next, the attacker looks for a default or stolen password to log in, an unpatched vulnerability or a misconfigured remote-access service. Sophisticated malware is not always necessary: In 2023, U.S. officials reported that Iranian-linked hackers targeted internet-connected Unitronics programmable logic controllers used by water utilities. Some utilities were still using the manufacturer’s default password , according to the Cybersecurity and Infrastructure Security Agency.

Finally, the attacker exploits the access they have gained. This could mean changing a password, issuing commands or attempting to alter the controller’s software. Researchers at the National Institute of Standards and Technology note that an intruder could replace legitimate control instructions with malicious commands. An attacker could also sneak into an office computer through phishing, then access the controller network.

Industrial equipment in service for decades is extremely vulnerable because it may not support modern security features, and utilities may delay updates because they want to avoid interrupting operations.

Reports thus far indicate that hackers accessed the Minnesota water systems through controllers that communicate over the internet directly. A July 30 FBI and Environmental Protection Agency advisory stated that attackers remotely accessed Rockwell Automation MicroLogix programmable logic controllers that were connected directly to the internet, and changed their IP addresses and passwords.

### Defensive moves that utilities can take

The most immediate step that utilities can take to protect themselves is to remove controllers and human dashboards from direct connection to the internet. Following the Minnesota attacks, the Cybersecurity and Infrastructure Security Agency urged water utilities to place this equipment behind properly configured firewalls and other safeguards.

When remote access is necessary, utilities should route communications through a secure gateway or VPN, require multiple levels of authentication, and limit how much access each user has. Utilities should change default passwords, disable unused remote-access services and install vendor-approved updates to connected equipment.

In their guidance on internet-exposed dashboards , the cybersecurity agency also recommends separating operational networks from email and other business systems. This measure makes it harder for attackers to move between the two systems.

Finally, utilities should back up controller programs, log remote-access activity and practice restoring systems and operating manually.

### A matter of resources

Rural water utilities with limited resources are a significant vulnerability in the United States’ critical infrastructure.

A group of volunteer cybersecurity experts is providing guidance to water utilities , but their reach is limited. Smaller utilities may need government funding or shared cybersecurity services to be able to defend themselves.

William Akoto does not work for, consult, own shares in or receive funding from any company or organization that would benefit from this article, and has disclosed no relevant affiliations beyond their academic appointment.

<img src="https://counter.theconversation.com/content/288864/count.gif" alt="" width="1" height="1">
