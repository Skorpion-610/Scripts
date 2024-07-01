# Importer les bibliothèques nécessaires pour Windows Forms
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Créer la fenêtre principale
$form = New-Object System.Windows.Forms.Form
$form.Text = "Toolbox"
$form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen

# Ajouter un label pour l'avertissement en haut de la toolbox
$labelWarning = New-Object System.Windows.Forms.Label
$labelWarning.Location = New-Object System.Drawing.Point(20, 20)
$labelWarning.Size = New-Object System.Drawing.Size(260, 50)
$labelWarning.Text = "Ce script doit être exécuté en tant qu'administrateur !"
$labelWarning.ForeColor = [System.Drawing.Color]::Red
$form.Controls.Add($labelWarning)

# Définir l'ordre des boutons
$buttonOrder = @(
    "button3",
    "button5",
    "button4",
    "button1",
    "button2"
)

# Créer un hashtable pour stocker les boutons
$buttons = @{
    "button1" = New-Object System.Windows.Forms.Button
    "button2" = New-Object System.Windows.Forms.Button
    "button3" = New-Object System.Windows.Forms.Button
    "button4" = New-Object System.Windows.Forms.Button
    "button5" = New-Object System.Windows.Forms.Button
}

# Définir les propriétés et actions pour chaque bouton
$buttons["button1"].Size = New-Object System.Drawing.Size(260, 50)
$buttons["button1"].Text = "Créer OU et objets AD"
$buttons["button1"].Add_Click({
        $scriptContent = @'
# Import Active Directory module
Import-Module ActiveDirectory

# Fonction pour générer des noms aléatoires
function Get-RandomName($length) {
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    $name = -join ((65..90) + (97..122) | Get-Random -Count $length | ForEach-Object { [char]$_ })
    return $name
}

# Demande à l'utilisateur de spécifier le domaine
$domaine = Read-Host -Prompt "Entrez votre domaine (ex: exemple.com)"
$domaineComponents = $domaine.Split(".") | ForEach-Object { "DC=$_"}
$domainePath = ($domaineComponents -join ",")

# Création de l'OU principale
$rootOU = "OU=MonOrganisationTest,$domainePath"
New-ADOrganizationalUnit -Name "MonOrganisationTest" -Path $domainePath

# Création des sous-OU
$ouComputers = "OU=Ordinateurs,$rootOU"
$ouUsers = "OU=Utilisateurs,$rootOU"
New-ADOrganizationalUnit -Name "Ordinateurs" -Path $rootOU
New-ADOrganizationalUnit -Name "Utilisateurs" -Path $rootOU

# Nombre d'ordinateurs et d'utilisateurs à créer
$numberOfComputers = 5
$numberOfUsers = 5

# Création des ordinateurs avec des noms simples
for ($i = 1; $i -le $numberOfComputers; $i++) {
    $computerName = "Ordinateur-$i"
    New-ADComputer -Name $computerName -Path $ouComputers -AccountPassword (ConvertTo-SecureString "P@ssw0rd" -AsPlainText -Force) -Enabled $true
}

# Création des utilisateurs avec des noms simples
for ($i = 1; $i -le $numberOfUsers; $i++) {
    $firstName = "Utilisateur"
    $lastName = "$i"
    $userName = $firstName + "-" + $lastName
    $password = "P@ssw0rd" + (Get-Random -Minimum 1000 -Maximum 9999) # Mot de passe de base, à personnaliser si nécessaire

    New-ADUser -GivenName $firstName -Surname $lastName -Name $userName -SamAccountName $userName -UserPrincipalName "$userName@$domaine" -Path $ouUsers -AccountPassword (ConvertTo-SecureString $password -AsPlainText -Force) -Enabled $true
}

Write-Host "OU et objets créés avec succès."
Read-Host -Prompt "Appuyez sur une touche pour quitter"
'@

        $tempFile = [System.IO.Path]::GetTempFileName()
        $tempFile = [System.IO.Path]::ChangeExtension($tempFile, ".ps1")
        [System.IO.File]::WriteAllText($tempFile, $scriptContent)

        Start-Process powershell -ArgumentList "-NoExit", "-File", $tempFile
    })

$buttons["button2"].Size = New-Object System.Drawing.Size(260, 50)
$buttons["button2"].Text = "Afficher utilisateurs AD"
$buttons["button2"].Add_Click({
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing

        # Créer une DataTable pour stocker les résultats
        $dataTable = New-Object System.Data.DataTable
        $dataTable.Columns.Add("Nom du compte", [string])
        $dataTable.Columns.Add("Date de création", [string])
        $dataTable.Columns.Add("Membre de", [string])

        # Récupérer les utilisateurs et leurs propriétés
        $users = Get-ADUser -Filter * -Properties Name, WhenCreated, MemberOf
        foreach ($user in $users) {
            $c = $user.WhenCreated.ToString('dd/MM/yyyy HH:mm')
            $d = ($user.MemberOf | Get-ADGroup).Name -join ', '

            # Ajouter les données à la DataTable
            $row = $dataTable.NewRow()
            $row["Nom du compte"] = $user.Name
            $row["Date de création"] = $c
            $row["Membre de"] = $d
            $dataTable.Rows.Add($row)
        }

        # Créer le formulaire Windows Forms
        $form = New-Object System.Windows.Forms.Form
        $form.Text = "Informations des utilisateurs AD"
        $form.Size = New-Object System.Drawing.Size(800, 600)
        $form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen

        # Créer le DataGridView pour afficher les résultats
        $dataGridView = New-Object System.Windows.Forms.DataGridView
        $dataGridView.Size = New-Object System.Drawing.Size(780, 550)
        $dataGridView.Location = New-Object System.Drawing.Point(10, 10)
        $dataGridView.DataSource = $dataTable
        $dataGridView.AutoSizeColumnsMode = 'AllCells'

        # Ajouter le DataGridView au formulaire
        $form.Controls.Add($dataGridView)

        # Afficher le formulaire
        $form.Add_Shown({ $form.Activate() })
        [void]$form.ShowDialog()
    })

$buttons["button3"].Size = New-Object System.Drawing.Size(260, 50)
$buttons["button3"].Text = "1. Exécuter Sysprep"
$buttons["button3"].Add_Click({
        $sysprepScript = @'
# Vérifier si le script est exécuté en tant qu'administrateur
If (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Warning "Vous devez exécuter ce script en tant qu'administrateur !"
    Exit
}

# Demander confirmation à l'utilisateur
$confirmation = Read-Host "Voulez-vous vraiment exécuter Sysprep sur ce serveur ? (o/n)"
if ($confirmation -ne "o") {
    Write-Output "Opération annulée."
    Exit
}

# Demander à l'utilisateur de choisir entre reboot et shutdown
$action = Read-Host "Que souhaitez-vous faire après Sysprep ? (Reboot/Shutdown) (r/s)"
switch ($action) {
    "r" { $sysprepArgs = "/oobe /generalize /reboot" }
    "s" { $sysprepArgs = "/oobe /generalize /shutdown" }
    default {
        Write-Output "Choix non valide. Opération annulée."
        Exit
    }
}

# Chemin vers l'exécutable Sysprep
$sysprepPath = "$env:SystemRoot\System32\Sysprep\sysprep.exe"

# Vérifier si Sysprep existe
if (-Not (Test-Path $sysprepPath)) {
    Write-Error "Sysprep n'a pas été trouvé sur ce système."
    Exit
}

# Exécuter Sysprep avec les options choisies
try {
    Start-Process -FilePath $sysprepPath -ArgumentList $sysprepArgs -Wait -NoNewWindow
    Write-Output "Sysprep a été exécuté avec succès."
} catch {
    Write-Error "Erreur lors de l'exécution de Sysprep : $_"
    Exit
}

# Fermer la session PowerShell
Exit
'@

        $tempFile = [System.IO.Path]::GetTempFileName()
        $tempFile = [System.IO.Path]::ChangeExtension($tempFile, ".ps1")
        [System.IO.File]::WriteAllText($tempFile, $sysprepScript)

        Start-Process powershell -ArgumentList "-NoExit", "-File", $tempFile
    })

$buttons["button4"].Size = New-Object System.Drawing.Size(260, 50)
$buttons["button4"].Text = "3. Joindre au domaine"
$buttons["button4"].Add_Click({
        $domainScript = @'
# Demander le domaine à joindre à l'utilisateur
$domainName = Read-Host "Entrez le nom du domaine auquel vous souhaitez joindre cette machine"

# Demander le nom d'utilisateur du domaine avec les privilèges d'ajout de machine
$domainUser = Read-Host "Entrez le nom d'utilisateur du domaine (format: domaine\utilisateur)"

# Demander le mot de passe de l'utilisateur du domaine
$domainPassword = Read-Host "Entrez le mot de passe de l'utilisateur du domaine" -AsSecureString

# Convertir le mot de passe en texte clair (attention : manipulez avec précaution)
$domainPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($domainPassword))

# Joindre la machine au domaine
Add-Computer -DomainName $domainName -Credential (New-Object System.Management.Automation.PSCredential($domainUser, $domainPassword)) -Force

# Demande de confirmation avant redémarrage
$confirmRestart = Read-Host "La machine a été jointe au domaine $domainName. Voulez-vous redémarrer maintenant? (o/n)"

if ($confirmRestart -match '^(Oui|oui|O|o|Yes|yes|Y|y)$') {
    Restart-Computer
    Write-Host "La machine va redémarrer..."
} else {
    Write-Host "Le redémarrage a été annulé. Veuillez redémarrer la machine manuellement pour appliquer les modifications."
}

'@

        $tempFile = [System.IO.Path]::GetTempFileName()
        $tempFile = [System.IO.Path]::ChangeExtension($tempFile, ".ps1")
        [System.IO.File]::WriteAllText($tempFile, $domainScript)

        Start-Process powershell -ArgumentList "-NoExit", "-File", $tempFile
    })

$buttons["button5"].Size = New-Object System.Drawing.Size(260, 50)
$buttons["button5"].Text = "2. Renommer l'ordinateur"
$buttons["button5"].Add_Click({
        $scriptContent = @'

# Demander à l'utilisateur le nouveau nom de l'ordinateur
$NewName = Read-Host "Entrez le nouveau nom de l'ordinateur"

# Renommer l'ordinateur
Rename-Computer -NewName $NewName

# Demander à l'utilisateur s'il souhaite redémarrer l'ordinateur maintenant
$restartChoice = Read-Host "Voulez-vous redémarrer l'ordinateur maintenant ? (o/n)"
if ($restartChoice -eq "O" -or $restartChoice -eq "o") {
    Restart-Computer -Force
} else {
    Write-Output "Le redémarrage de l'ordinateur n'a pas été effectué."
}
'@

        $tempFile = [System.IO.Path]::GetTempFileName()
        $tempFile = [System.IO.Path]::ChangeExtension($tempFile, ".ps1")
        [System.IO.File]::WriteAllText($tempFile, $scriptContent)

        Start-Process powershell -ArgumentList "-NoExit", "-File", $tempFile
    })

# Variable pour suivre la position verticale des boutons
$currentY = 90  # Position verticale initiale pour le premier bouton

# Ajouter les boutons à la fenêtre principale selon l'ordre défini
foreach ($buttonName in $buttonOrder) {
    $button = $buttons[$buttonName]
    $button.Location = New-Object System.Drawing.Point(20, $currentY)
    $form.Controls.Add($button)
    $currentY += $button.Height + 10
}

# Fonction pour ajuster automatiquement la taille de la fenêtre en fonction des boutons ajoutés
function AutoSizeForm {
    $formHeight = $currentY + $buttons["button5"].Height + 40  # Hauteur totale des boutons + espace supplémentaire
    $form.ClientSize = New-Object System.Drawing.Size(300, $formHeight)
}

# Appeler la fonction pour ajuster la taille de la fenêtre
AutoSizeForm

# Afficher la fenêtre principale
$form.Add_Shown({ $form.Activate() })
[void]$form.ShowDialog()