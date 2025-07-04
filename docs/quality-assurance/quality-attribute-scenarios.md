# Quality attribute scenarios
## Maintainability
### Modifiability
**Importance:** with the beginning of each semester, the course scheduling inevitably changes, that is why
the plugin should be capable of being swiftly modified to satisfy the current
semester needs.
#### Test "MODIF-1"
> **Source:** 
> 
> **Stimulus:** 
> 
> **Artifact:** 
> 
> **Environment:**
> 
> **Response:** 
> 
> **Response Measure:**

To execute **"MODIF-1"**, we will....

#### Test "MODIF-2"
> **Source:** 
> 
> **Stimulus:** 
> 
> **Artifact:** 
> 
> **Environment:**
> 
> **Response:** 
> 
> **Response Measure:**

To execute **"MODIF-2"**, we will....

## Security
### Confidentiality
**Importance:** fellow Innopolis University students should not be able to view the staff's plugin
out of confidentiality and security policies accepted in the University.
#### Test "CONF-1"
> **Source:** Unknown user (not Innopolis University staff)
> 
> **Stimulus:** Access plugin services
> 
> **Artifact:** Data produced/consumed by the plugin
> 
> **Environment:** Normal mode
> 
> **Response:** Prohibition of plugin usage
> 
> **Response Measure:** 0% of data loss, <10 seconds error response

To execute **"CONF-1"**, we will log out of whitelisted Innopolis University
accounts and simulate the unknown user scenario.

## Interaction capability
### Self-descriptiveness
**Importance:** future staff should be able to effortlessly apply the plugin to scheduling conflicts and not
spend time on remembering the functionality of a specific undocumented part of plugin interface.
#### Test "S-DESC-1"
> **Source:** Authorized user (Innopolis University staff) 
> 
> **Stimulus:** Access plugin services, check readability of plugin's interface elements
> 
> **Artifact:** Interface elements descriptions (buttons, icons, etc.)
> 
> **Environment:** Normal mode
> 
> **Response:** Successful usage of plugin (pages returning) upon understanding all interface elements descriptions
> 
> **Response Measure:** <10 seconds collisions fetching

To execute **"S-DESC-1"**, we will ask a non-affiliated staff member to test our application
without explaining how the functionality works.

#### Test "S-DESC-2"
> **Source:** Authorized user (Innopolis University staff) 
> 
> **Stimulus:** Check whether upon interaction with UI intended events occur
> 
> **Artifact:** UI elements (buttons, icons, etc.)
> 
> **Environment:** Normal mode
> 
> **Response:** Successful usage of plugin (pages returning) upon understanding all interface elements descriptions
> 
> **Response Measure:** <10 seconds collisions fetching

To execute **"S-DESC-2"**, we will ask a non-affiliated staff member to test our application
without explaining how the functionality works.